import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from agency.models import CompanyInformation
from agency.serializers import CompanyInformationDetailSerializer

company = CompanyInformation.objects.first()
serializer = CompanyInformationDetailSerializer(company)
print("Company images:", serializer.data.get('images', []))
