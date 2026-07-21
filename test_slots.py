import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from staff.models import Staff, StaffMonthlySlot
from staff.selectors import get_public_current_month_staff_slots
from django.utils import timezone

all_staff = Staff.objects.all()
print("Total staff:", all_staff.count())

slots = get_public_current_month_staff_slots()
print("Slots returned:", slots.count())

for s in all_staff:
    print(s.user.get_full_name(), "- Active:", s.is_active, "- Office:", s.office)

for s in slots:
    print("Slot for:", s.staff.user.get_full_name(), s.total_slot)
