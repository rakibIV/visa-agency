import django_filters

from agency.models import Office

from .models import (
    Designation,
    Staff,
)


class StaffFilter(django_filters.FilterSet):
    designation = django_filters.ModelChoiceFilter(
        queryset=Designation.objects.filter(
            is_active=True,
        ),
    )

    office = django_filters.ModelChoiceFilter(
        queryset=Office.objects.filter(
            is_active=True,
        ),
    )

    gender = django_filters.CharFilter()

    nationality = django_filters.CharFilter(
        lookup_expr="icontains",
    )

    joining_date_after = django_filters.DateFilter(
        field_name="joining_date",
        lookup_expr="gte",
    )

    joining_date_before = django_filters.DateFilter(
        field_name="joining_date",
        lookup_expr="lte",
    )

    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Staff

        fields = [
            "designation",
            "office",
            "gender",
            "nationality",
            "is_active",
        ]
