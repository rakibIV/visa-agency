import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from agency.models import ContactUs
from django.contrib.auth import get_user_model

User = get_user_model()

c = ContactUs.objects.first()
if c:
    print("Before:", c.is_read)
    from rest_framework.test import APIClient
    
    admin = User.objects.filter(is_superuser=True).first()
    client = APIClient()
    client.force_authenticate(user=admin)
    
    response = client.patch(f'/api/contact-us/{c.id}/', {'is_read': True}, format='json')
    print("Response Status:", response.status_code)
    print("Response Data:", response.data)
    
    c.refresh_from_db()
    print("After:", c.is_read)
else:
    print("No contact messages found.")
