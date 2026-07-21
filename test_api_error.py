import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from django.utils import timezone
from django.db.models import Prefetch, Count
from staff.models import Staff, StaffMonthlySlot
from api.public_serializers import PublicStaffMonthlySlotSerializer

month_start = timezone.localdate().replace(day=1)
slots = StaffMonthlySlot.objects.filter(allocation_month=month_start).annotate(
    used_slot_count=Count('applicants')
)
staff_qs = Staff.objects.filter(is_active=True).prefetch_related(
    Prefetch('monthly_slots', queryset=slots, to_attr='current_month_slots')
)

try:
    data = PublicStaffMonthlySlotSerializer(staff_qs, many=True).data
    print(data)
except Exception as e:
    import traceback
    traceback.print_exc()
