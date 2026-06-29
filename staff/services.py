from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Staff
from .utils import _generate_employee_id

User = get_user_model()


@transaction.atomic
def create_staff(
    *,
    first_name,
    last_name,
    email,
    password,
    staff_data,
):
    """
    Creates both the Django User account and the Staff profile.
    """

    employee_id = _generate_employee_id()

    user = User.objects.create_user(
        username=employee_id,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )

    user.is_active = staff_data.get(
        "is_active",
        True,
    )

    user.save(
        update_fields=[
            "is_active",
        ]
    )

    staff = Staff.objects.create(
        user=user,
        employee_id=employee_id,
        **staff_data,
    )

    return staff


@transaction.atomic
def update_staff(
    *,
    staff,
    first_name,
    last_name,
    email,
    new_password=None,
    staff_data,
):
    """
    Updates both the Django User account and the Staff profile.
    """

    user = staff.user

    user.first_name = first_name
    user.last_name = last_name
    user.email = email

    if new_password:
        user.set_password(new_password)

    user.save()

    for field, value in staff_data.items():
        setattr(
            staff,
            field,
            value,
        )

    staff.save()

    if "is_active" in staff_data:
        user.is_active = staff.is_active
        user.save(
            update_fields=[
                "is_active",
            ]
        )

    return staff


@transaction.atomic
def reset_staff_password(
    *,
    staff,
    new_password,
):
    """
    Resets a staff member's login password.
    """

    user = staff.user
    user.set_password(new_password)
    user.save()


@transaction.atomic
def activate_staff(
    *,
    staff,
):
    """
    Activates a staff member.
    """

    staff.is_active = True
    staff.save(
        update_fields=[
            "is_active",
        ]
    )

    staff.user.is_active = True
    staff.user.save(
        update_fields=[
            "is_active",
        ]
    )


@transaction.atomic
def deactivate_staff(
    *,
    staff,
):
    """
    Deactivates a staff member.
    """

    staff.is_active = False
    staff.save(
        update_fields=[
            "is_active",
        ]
    )

    staff.user.is_active = False
    staff.user.save(
        update_fields=[
            "is_active",
        ]
    )
