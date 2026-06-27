import django_filters

from .models import Country


class CountryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )

    code = django_filters.CharFilter(
        field_name="code",
        lookup_expr="iexact",
    )

    is_featured = django_filters.BooleanFilter()

    class Meta:
        model = Country
        fields = [
            "name",
            "code",
            "is_featured",
        ]


