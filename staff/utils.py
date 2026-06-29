from django.forms.models import model_to_dict

from .models import Staff


def _generate_employee_id():
    """
    Generates the next employee ID.

    Example:
        EMP-0001
        EMP-0002
        EMP-0003
    """

    last_staff = (
        Staff.objects.only("employee_id")
        .order_by("-created_at")
        .first()
    )

    if last_staff is None:
        return "EMP-0001"

    last_number = int(
        last_staff.employee_id.replace(
            "EMP-",
            "",
        )
    )

    return f"EMP-{last_number + 1:04d}"


def get_staff_data(staff):
    """
    Returns all editable Staff fields as a dictionary.

    Useful for services, admin, serializers,
    tests and future APIs.
    """

    return model_to_dict(
        staff,
        exclude=[
            "id",
            "user",
            "employee_id",
            "created_at",
            "updated_at",
        ],
    )
