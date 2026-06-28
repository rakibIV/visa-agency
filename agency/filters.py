import django_filters

from .models import AgencyService


class AgencyServiceFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
    )

    is_featured = django_filters.BooleanFilter()

    class Meta:
        model = AgencyService
        fields = [
            "title",
            "is_featured",
        ]