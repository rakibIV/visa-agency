import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from agency.models import AgencyImage
from agency.serializers import AgencyImageSerializer

img = AgencyImage.objects.first()
# Note: we need to pass context={'request': request} for absolute URLs normally.
# Let's see what the serializer returns WITHOUT request context.
print(AgencyImageSerializer(img).data)
