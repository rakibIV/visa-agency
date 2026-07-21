import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from agency.models import ContactUs, ApplicationRequest

unread = ContactUs.objects.filter(is_read=False, is_active=True).count()
pending = ApplicationRequest.objects.filter(status='PENDING').count()

print(f"UNREAD: {unread}")
print(f"PENDING: {pending}")
