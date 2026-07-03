from datetime import timedelta
from decimal import Decimal, InvalidOperation
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import CurrencyRate


DEFAULT_TARGET_CURRENCY = getattr(
    settings,
    "CURRENCY_RATE_TARGET_CURRENCY",
    "EUR",
)

DEFAULT_MAX_AGE_HOURS = getattr(
    settings,
    "CURRENCY_RATE_MAX_AGE_HOURS",
    24,
)


class CurrencyFreaksException(Exception):
    """
    Raised when exchange rate fetch fails.
    """


def _normalize_currency_code(currency):
    if not currency:
        raise CurrencyFreaksException(
            "Currency code is required."
        )

    return str(currency).strip().upper()


def _is_fresh(currency_rate, max_age_hours):
    age = timezone.now() - currency_rate.fetched_at
    return age <= timedelta(hours=max_age_hours)


def _fetch_rate_from_api(
    from_currency,
    to_currency,
):
    url = "https://api.currencyfreaks.com/v2.0/rates/latest"

    params = {
        "apikey": settings.CURRENCY_FREAKS_API_KEY,
        "symbols": f"{from_currency},{to_currency}",
    }

    try:
        request = Request(
            f"{url}?{urlencode(params)}",
            headers={
                "Accept": "application/json",
            },
        )

        with urlopen(request, timeout=15) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )
    except (HTTPError, URLError, json.JSONDecodeError, TimeoutError) as exc:
        raise CurrencyFreaksException(
            "Failed to connect to Currency Freaks."
        ) from exc

    rates = data.get("rates", {})
    from_rate = rates.get(from_currency)
    to_rate = rates.get(to_currency)

    if not from_rate or not to_rate:
        raise CurrencyFreaksException(
            "Currency rate not found in API response."
        )

    try:
        from_rate = Decimal(from_rate)
        to_rate = Decimal(to_rate)
    except (InvalidOperation, TypeError) as exc:
        raise CurrencyFreaksException(
            "Invalid currency rate received."
        ) from exc

    if from_rate == 0:
        raise CurrencyFreaksException(
            "Invalid base currency rate."
        )

    exchange_rate = (
        to_rate / from_rate
    ).quantize(
        Decimal("0.0001")
    )

    return exchange_rate, data


@transaction.atomic
def refresh_exchange_rate(
    from_currency,
    to_currency=DEFAULT_TARGET_CURRENCY,
):
    from_currency = _normalize_currency_code(from_currency)
    to_currency = _normalize_currency_code(to_currency)

    if from_currency == to_currency:
        rate_value = Decimal("1.0000")
        raw_response = {
            "rates": {
                from_currency: "1",
                to_currency: "1",
            }
        }
    else:
        rate_value, raw_response = _fetch_rate_from_api(
            from_currency=from_currency,
            to_currency=to_currency,
        )

    currency_rate, _ = CurrencyRate.objects.update_or_create(
        base_currency=from_currency,
        target_currency=to_currency,
        defaults={
            "rate": rate_value,
            "source": "CurrencyFreaks",
            "fetched_at": timezone.now(),
            "raw_response": raw_response,
        },
    )

    return currency_rate


def get_exchange_rate(
    from_currency,
    to_currency=DEFAULT_TARGET_CURRENCY,
    *,
    refresh=False,
    max_age_hours=DEFAULT_MAX_AGE_HOURS,
):
    """
    Returns a database-backed exchange rate.

    The flow is:
    1. Use the cached value if it is still fresh.
    2. Refresh from Currency Freaks when missing/stale or when requested.
    3. Fall back to the cached value if the API is temporarily unavailable.
    """

    from_currency = _normalize_currency_code(from_currency)
    to_currency = _normalize_currency_code(to_currency)

    cached_rate = (
        CurrencyRate.objects.filter(
            base_currency=from_currency,
            target_currency=to_currency,
        )
        .order_by("-fetched_at")
        .first()
    )

    if cached_rate and not refresh and _is_fresh(
        cached_rate,
        max_age_hours,
    ):
        return cached_rate.rate

    if from_currency == to_currency:
        try:
            refreshed_rate = refresh_exchange_rate(
                from_currency=from_currency,
                to_currency=to_currency,
            )
            return refreshed_rate.rate
        except CurrencyFreaksException:
            if cached_rate:
                return cached_rate.rate

            return Decimal("1.0000")

    try:
        refreshed_rate = refresh_exchange_rate(
            from_currency=from_currency,
            to_currency=to_currency,
        )
        return refreshed_rate.rate
    except CurrencyFreaksException:
        if cached_rate:
            return cached_rate.rate

        raise


def sync_currency_rates(
    currencies,
    to_currency=DEFAULT_TARGET_CURRENCY,
    *,
    force=False,
    max_age_hours=DEFAULT_MAX_AGE_HOURS,
):
    """
    Refreshes and stores currency rates for the provided codes.
    """

    synced_rates = []

    for currency in currencies:
        normalized_currency = _normalize_currency_code(currency)

        if normalized_currency == _normalize_currency_code(to_currency):
            continue

        cached_rate = (
            CurrencyRate.objects.filter(
                base_currency=normalized_currency,
                target_currency=_normalize_currency_code(to_currency),
            )
            .order_by("-fetched_at")
            .first()
        )

        if cached_rate and not force and _is_fresh(
            cached_rate,
            max_age_hours,
        ):
            synced_rates.append(cached_rate)
            continue

        synced_rates.append(
            refresh_exchange_rate(
                from_currency=normalized_currency,
                to_currency=to_currency,
            )
        )

    return synced_rates
