import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from agency.serializers import ContactUsSerializer

print("Meta read_only_fields:", getattr(ContactUsSerializer.Meta, 'read_only_fields', None))
