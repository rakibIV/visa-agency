from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)

from .filters import CountryFilter
from .models import Country
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CountrySerializer,
    CountryDetailSerializer,
)


class CountryListAPIView(ListAPIView):
    queryset = Country.objects.filter(
        is_active=True,
    )

    serializer_class = CountrySerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = CountryFilter

    search_fields = [
        "name",
        "code",
        "nationality",
    ]

    ordering_fields = [
        "name",
        "display_order",
        "created_at",
    ]

    ordering = [
        "display_order",
        "name",
    ]


class CountryDetailAPIView(RetrieveAPIView):
    queryset = Country.objects.filter(
        is_active=True,
    )

    serializer_class = CountryDetailSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    lookup_field = "slug"


class CountryCreateAPIView(CreateAPIView):
    queryset = Country.objects.all()

    serializer_class = CountryDetailSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]


class CountryUpdateAPIView(UpdateAPIView):
    queryset = Country.objects.all()

    serializer_class = CountryDetailSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]


class CountryDeleteAPIView(DestroyAPIView):
    queryset = Country.objects.all()

    permission_classes = [
        IsAdminOrReadOnly,
    ]