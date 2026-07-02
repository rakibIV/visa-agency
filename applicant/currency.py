from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings


class CurrencyFreaksException(Exception):
    """
    Raised when exchange rate fetch fails.
    """
    pass


def get_exchange_rate(
    from_currency,
    to_currency="EUR",
):
    """
    Fetches live exchange rate from Currency Freaks.

    Example:
        get_exchange_rate("USD")
        -> Decimal("0.9234")

        get_exchange_rate("GBP", "EUR")
        -> Decimal("1.1732")
    """

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return Decimal("1.0000")

    url = "https://api.currencyfreaks.com/v2.0/rates/latest"

    params = {
        "apikey": settings.CURRENCY_FREAKS_API_KEY,
        "symbols": f"{from_currency},{to_currency}",
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as exc:
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

    # Currency Freaks returns rates against USD by default.
    # To get direct FROM -> TO conversion:
    # rate = to_rate / from_rate
    exchange_rate = (
        to_rate / from_rate
    ).quantize(
        Decimal("0.0001")
    )

    return exchange_rate