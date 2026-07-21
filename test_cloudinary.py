import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from agency.models import AgencyImage
from agency.serializers import AgencyImageSerializer

img = AgencyImage.objects.first()
if img:
    print("Found AgencyImage ID:", img.id)
    print("Direct URL:", getattr(img.image, 'url', 'NO URL'))
    serializer = AgencyImageSerializer(img)
    print("Serialized data:", serializer.data)
else:
    print("No AgencyImage found.")
