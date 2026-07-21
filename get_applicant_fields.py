import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from applicant.models import ApplicantProfile

print("Fields for ApplicantProfile:")
for f in ApplicantProfile._meta.fields:
    print(f.name, "blank:", f.blank, "null:", f.null)
