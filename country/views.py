from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404

from .models import (
    Country,
    CountryFAQ,
    CountryGallery,
    CountryRequirement,
    CountrySEO,
)

from .filters import CountryFilter
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CountrySerializer,
    CountryDetailSerializer,
    CountryFAQSerializer,
    CountryGallerySerializer,
    CountryRequirementSerializer,
    CountrySEOSerializer,
)


class CountryViewSet(ModelViewSet):
    queryset = Country.objects.filter(
        is_active=True,
    )

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
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

    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CountryDetailSerializer
        return CountrySerializer

    def get_queryset(self):
        if self.action == "retrieve":
            return (
                Country.objects
                .filter(is_active=True)
                .prefetch_related(
                    "requirements",
                    "faqs",
                    "gallery",
                )
                .select_related(
                    "seo",
                )
            )

        return Country.objects.filter(
            is_active=True,
        )
    


class CountryNestedViewSetMixin:
    def get_country(self):
        country_value = self.kwargs.get("country_slug") or self.kwargs.get("country_pk")
        if not country_value:
            raise ValueError("Country identifier is missing from the nested URL")
        return get_object_or_404(Country, slug=country_value)


class CountryFAQViewSet(CountryNestedViewSetMixin, ModelViewSet):
    serializer_class = CountryFAQSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return CountryFAQ.objects.filter(country=self.get_country())

    def perform_create(self, serializer):
        serializer.save(country=self.get_country())


class CountryGalleryViewSet(CountryNestedViewSetMixin, ModelViewSet):
    serializer_class = CountryGallerySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return CountryGallery.objects.filter(country=self.get_country())

    def perform_create(self, serializer):
        serializer.save(country=self.get_country())


class CountryRequirementViewSet(CountryNestedViewSetMixin, ModelViewSet):
    serializer_class = CountryRequirementSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["requirement_type"]  # Handled country filtering via URL route instead

    def get_queryset(self):
        return CountryRequirement.objects.filter(country=self.get_country())

    def perform_create(self, serializer):
        serializer.save(country=self.get_country())





class CountrySEOViewSet(ModelViewSet):
    queryset = CountrySEO.objects.all()
    serializer_class = CountrySEOSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country']
