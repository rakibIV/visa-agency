import django_filters

from .models import Visa


class VisaFilter(django_filters.FilterSet):
    country = django_filters.UUIDFilter(
        field_name="country__id",
    )

    category = django_filters.UUIDFilter(
        field_name="category__id",
    )

    is_featured = django_filters.BooleanFilter()

    from_any_country = django_filters.BooleanFilter()

    class Meta:
        model = Visa
        fields = [
            "country",
            "category",
            "is_featured",
            "from_any_country",
        ]


import django_filters

from .models import VisaJob


class VisaJobFilter(django_filters.FilterSet):

    minimum_salary = django_filters.NumberFilter(
        field_name="minimum_salary",
        lookup_expr="gte",
    )

    maximum_salary = django_filters.NumberFilter(
        field_name="maximum_salary",
        lookup_expr="lte",
    )

    overtime_available = django_filters.BooleanFilter()

    is_featured = django_filters.BooleanFilter()

    class Meta:
        model = VisaJob

        fields = [
            "minimum_salary",
            "maximum_salary",
            "overtime_available",
            "is_featured",
        ]