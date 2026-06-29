from django.db.models import Prefetch

from .models import (
    Staff,
    StaffDocument,
    StaffEmergencyContact,
    StaffMonthlySlot,
)


def get_staff_queryset():
    """
    Base queryset for Staff.
    """

    return (
        Staff.objects.select_related(
            "user",
            "designation",
            "office",
            "reference_staff",
        )
        .prefetch_related(
            Prefetch(
                "monthly_slots",
                queryset=StaffMonthlySlot.objects.order_by(
                    "-allocation_month",
                ),
            ),
            Prefetch(
                "documents",
                queryset=StaffDocument.objects.filter(
                    is_active=True,
                ).order_by(
                    "display_order",
                ),
            ),
            Prefetch(
                "emergency_contacts",
                queryset=StaffEmergencyContact.objects.order_by(
                    "name",
                ),
            ),
        )
    )


def get_active_staff():
    """
    Returns all active staff.
    """

    return get_staff_queryset().filter(
        is_active=True,
    )


def get_staff_by_employee_id(
    employee_id,
):
    """
    Returns a single Staff object by employee ID.
    """

    return get_staff_queryset().get(
        employee_id=employee_id,
    )


def get_staff_by_user(
    user,
):
    """
    Returns Staff profile for the authenticated user.
    """

    return get_staff_queryset().get(
        user=user,
    )


def get_staff_monthly_slots(
    staff,
):
    """
    Returns all monthly slot allocations.
    """

    return (
        staff.monthly_slots
        .all()
        .order_by(
            "-allocation_month",
        )
    )


def get_staff_documents(
    staff,
):
    """
    Returns active documents.
    """

    return (
        staff.documents
        .filter(
            is_active=True,
        )
        .order_by(
            "display_order",
        )
    )


def get_staff_emergency_contacts(
    staff,
):
    """
    Returns emergency contacts.
    """

    return (
        staff.emergency_contacts
        .all()
        .order_by(
            "name",
        )
    )
