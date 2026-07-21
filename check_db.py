import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from agency.models import ContactUs

total = ContactUs.objects.count()
read_count = ContactUs.objects.filter(is_read=True).count()

print(f"Total: {total}, Read: {read_count}")
