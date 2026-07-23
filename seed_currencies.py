import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Visa_Web_Service.settings")
django.setup()

from core.models import Currency

currencies = [
    {"name": "Euro", "code": "EUR", "symbol": "€"},
    {"name": "US Dollar", "code": "USD", "symbol": "$"},
    {"name": "Bangladeshi Taka", "code": "BDT", "symbol": "৳"},
    {"name": "British Pound", "code": "GBP", "symbol": "£"},
    {"name": "Indian Rupee", "code": "INR", "symbol": "₹"},
    {"name": "United Arab Emirates Dirham", "code": "AED", "symbol": "د.إ"},
]

for c in currencies:
    Currency.objects.get_or_create(code=c["code"], defaults={"name": c["name"], "symbol": c["symbol"]})

print("Currencies seeded.")
