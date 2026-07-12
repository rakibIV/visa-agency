from decimal import Decimal, InvalidOperation
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings

DEFAULT_TARGET_CURRENCY = getattr(
    settings,
    "CURRENCY_RATE_TARGET_CURRENCY",
    "EUR",
)

class CurrencyFreaksException(Exception):
    """
    Raised when exchange rate fetch fails.
    """

def _normalize_currency_code(currency):
    if not currency:
        raise CurrencyFreaksException("Currency code is required.")
    return str(currency).strip().upper()

def _fetch_rate_from_api(from_currency, to_currency):
    url = "https://api.currencyfreaks.com/v2.0/rates/latest"
    params = {
        "apikey": settings.CURRENCY_FREAKS_API_KEY,
        "symbols": f"{from_currency},{to_currency}",
    }

    try:
        request = Request(
            f"{url}?{urlencode(params)}",
            headers={"Accept": "application/json"},
        )
        with urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, json.JSONDecodeError, TimeoutError) as exc:
        raise CurrencyFreaksException("Failed to connect to Currency Freaks.") from exc

    rates = data.get("rates", {})
    from_rate = rates.get(from_currency)
    to_rate = rates.get(to_currency)

    if not from_rate or not to_rate:
        raise CurrencyFreaksException("Currency rate not found in API response.")

    try:
        from_rate = Decimal(from_rate)
        to_rate = Decimal(to_rate)
    except (InvalidOperation, TypeError) as exc:
        raise CurrencyFreaksException("Invalid currency rate received.") from exc

    if from_rate == 0:
        raise CurrencyFreaksException("Invalid base currency rate.")

    exchange_rate = (to_rate / from_rate).quantize(Decimal("0.0001"))
    return exchange_rate

def get_exchange_rate(from_currency, to_currency=DEFAULT_TARGET_CURRENCY, **kwargs):
    """
    Fetches and returns the real-time exchange rate directly from the API.
    """
    from_currency = _normalize_currency_code(from_currency)
    to_currency = _normalize_currency_code(to_currency)

    if from_currency == to_currency:
        return Decimal("1.0000")

    return _fetch_rate_from_api(from_currency, to_currency)
