import django
import os
import sys

# Set up Django
sys.path.append('.')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Visa_Web_Service.settings")
django.setup()

import staff.serializers as ss
import applicant.serializers as a_s
import visa.serializers as v_s
import country.serializers as c_s

print("\n=== STAFF DETAIL ===")
for f in ss.StaffDetailSerializer().fields.keys():
    print(f)

print("\n=== APPLICANT DETAIL ===")
for f in a_s.ApplicantDetailSerializer().fields.keys():
    print(f)

print("\n=== VISA DETAIL ===")
for f in v_s.VisaDetailSerializer().fields.keys():
    print(f)

print("\n=== COUNTRY DETAIL ===")
for f in c_s.CountryDetailSerializer().fields.keys():
    print(f)
