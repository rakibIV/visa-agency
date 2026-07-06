from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from agency.models import CompanyInformation, Office
from .models import Designation, Staff, StaffMonthlySlot, SubStaff, SubStaffMonthlySlot


class SubStaffMonthlySlotTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.company = CompanyInformation.objects.create(
            company_name="Test Company",
            phone="123456789",
            address="Test Address",
        )
        self.office = Office.objects.create(
            company=self.company,
            branch_name="Head Office",
            phone="123456789",
            address="Test Address",
        )
        self.designation = Designation.objects.create(name="Senior Officer")

    def _create_staff(self):
        user = self.user_model.objects.create_user(
            username="staff-user",
            email="staff@example.com",
            password="password123",
            first_name="Alamin",
            last_name="Rahman",
        )
        return Staff.objects.create(
            user=user,
            employee_id="EMP-001",
            designation=self.designation,
            office=self.office,
            phone="01700000000",
            whatsapp="01700000000",
            father_name="Father",
            mother_name="Mother",
            gender="male",
            date_of_birth=date(1990, 1, 1),
            nationality="Bangladeshi",
            joining_date=date(2024, 1, 1),
            is_active=True,
        )

    def test_sub_staff_allocations_cannot_exceed_parent_staff_monthly_slots(self):
        staff = self._create_staff()
        month = date(2026, 7, 1)
        StaffMonthlySlot.objects.create(
            staff=staff,
            allocation_month=month,
            total_slot=10,
        )
        sub_staff_1 = SubStaff.objects.create(parent_staff=staff, name="Sub One")
        sub_staff_2 = SubStaff.objects.create(parent_staff=staff, name="Sub Two")

        SubStaffMonthlySlot.objects.create(
            sub_staff=sub_staff_1,
            allocation_month=month,
            allocated_slot=6,
        )

        with self.assertRaises(ValidationError):
            SubStaffMonthlySlot.objects.create(
                sub_staff=sub_staff_2,
                allocation_month=month,
                allocated_slot=5,
            )

    def test_sub_staff_slots_can_be_revoked_and_reassigned(self):
        staff = self._create_staff()
        month = date(2026, 7, 1)
        StaffMonthlySlot.objects.create(
            staff=staff,
            allocation_month=month,
            total_slot=8,
        )
        sub_staff_1 = SubStaff.objects.create(parent_staff=staff, name="Sub One")
        sub_staff_2 = SubStaff.objects.create(parent_staff=staff, name="Sub Two")

        allocation = SubStaffMonthlySlot.objects.create(
            sub_staff=sub_staff_1,
            allocation_month=month,
            allocated_slot=4,
        )

        allocation.allocated_slot = 0
        allocation.save()

        SubStaffMonthlySlot.objects.create(
            sub_staff=sub_staff_2,
            allocation_month=month,
            allocated_slot=4,
        )
