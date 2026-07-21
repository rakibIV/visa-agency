import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from agency.views import ContactUsViewSet
from agency.models import ContactUs
from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.filter(is_superuser=True).first()
c = ContactUs.objects.first()

if c and admin:
    factory = APIRequestFactory()
    request = factory.patch(f'/api/contact-us/{c.id}/', {'is_read': True}, format='json')
    force_authenticate(request, user=admin)
    
    view = ContactUsViewSet.as_view({'patch': 'partial_update'})
    response = view(request, pk=c.id)
    
    print("Response Status:", response.status_code)
    print("Response Data:", response.data)
    
    c.refresh_from_db()
    print("After:", c.is_read)
else:
    print("Missing admin or contact message.")
