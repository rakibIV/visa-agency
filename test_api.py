import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from staff.selectors import get_public_current_month_staff_slots
from api.public_serializers import PublicStaffMonthlySlotSerializer

slots = get_public_current_month_staff_slots()
serializer = PublicStaffMonthlySlotSerializer(slots, many=True)
print(serializer.data)
