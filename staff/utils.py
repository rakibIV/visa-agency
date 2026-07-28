import re
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
    emp_ids = list(Staff.objects.filter(employee_id__startswith="EMP-").values_list("employee_id", flat=True))
    existing_set = set(emp_ids)
    max_num = 0
    for eid in emp_ids:
        match = re.match(r"^EMP-(\d+)$", eid)
        if match:
            try:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass

    candidate_num = max_num + 1
    while f"EMP-{candidate_num:04d}" in existing_set:
        candidate_num += 1

    return f"EMP-{candidate_num:04d}"


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
