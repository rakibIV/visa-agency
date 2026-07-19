import os
import django
import sys

sys.path.append('f:/Rakib/Visa Agency Updated/visa-agency')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from country.models import Country

def populate_short_desc():
    countries = ["Portugal", "Netherlands", "Poland", "Bulgaria", "Serbia"]
    for c_name in countries:
        try:
            country = Country.objects.get(name=c_name)
            country.short_description = f"A golden opportunity to work legally in {c_name} and potentially obtain long-term residence with your family through our European Work Permit & Employment Assistance Program."
            country.save()
            print(f"Updated {c_name}")
        except Country.DoesNotExist:
            print(f"Skipping {c_name}")

if __name__ == "__main__":
    populate_short_desc()
