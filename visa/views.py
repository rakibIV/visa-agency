from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from .filters import VisaFilter, VisaJobFilter
from .models import (
    VisaCategory,
    Visa,
    VisaRequirement,
    VisaStep,
    VisaFAQ,
    VisaSEO,
    VisaJob,
    JobFacility,
)
from .permissions import IsAdminOrReadOnly
from .serializers import (
    VisaCategorySerializer,
    VisaSerializer,
    VisaDetailSerializer,
    VisaRequirementSerializer,
    VisaStepSerializer,
    VisaFAQSerializer,
    VisaSEOSerializer,
    VisaCreateUpdateSerializer,
    VisaJobSerializer,
    JobFacilitySerializer,
)


class VisaCategoryViewSet(ModelViewSet):
    queryset = VisaCategory.objects.all()

    serializer_class = VisaCategorySerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "name",
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


class VisaViewSet(ModelViewSet):
    queryset = (
        Visa.objects.select_related(
            "country",
            "category",
        )
        .prefetch_related(
            "services",
        )
    )

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = VisaFilter

    search_fields = [
        "name",
        "country__name",
        "category__name",
    ]

    ordering_fields = [
        "name",
        "display_order",
        "created_at",
        "minimum_salary",
        "maximum_salary",
    ]

    ordering = [
        "display_order",
        "name",
    ]

    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs.get(lookup_url_kwarg)

        queryset = self.filter_queryset(self.get_queryset())
        
        import uuid
        from django.db.models import Q
        try:
            uuid_obj = uuid.UUID(lookup_value)
            obj = get_object_or_404(queryset, Q(slug=lookup_value) | Q(pk=uuid_obj))
        except ValueError:
            obj = get_object_or_404(queryset, slug=lookup_value)
            
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):

        if self.action == "retrieve":
            return VisaDetailSerializer

        if self.action in [
            "create",
            "update",
            "partial_update",
        ]:
            return VisaCreateUpdateSerializer

        return VisaSerializer


class VisaNestedViewSetMixin:
    def get_visa(self):
        visa_value = self.kwargs.get("visa_slug") or self.kwargs.get("visa_pk")
        if not visa_value:
            raise ValueError("Visa identifier is missing from the nested URL")
        
        qs = Visa.objects.filter(slug=visa_value)
        if qs.exists():
            return qs.first()
            
        import uuid
        try:
            uuid_obj = uuid.UUID(visa_value)
            return get_object_or_404(Visa, pk=uuid_obj)
        except ValueError:
            return get_object_or_404(Visa, slug=visa_value)


class VisaRequirementViewSet(VisaNestedViewSetMixin, ModelViewSet):
    serializer_class = VisaRequirementSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_queryset(self):
        return VisaRequirement.objects.filter(
            visa=self.get_visa(),
        ).order_by(
            "display_order",
            "title",
        )

    def perform_create(self, serializer):
        serializer.save(
            visa=self.get_visa(),
        )


class VisaStepViewSet(VisaNestedViewSetMixin, ModelViewSet):
    serializer_class = VisaStepSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_queryset(self):
        return VisaStep.objects.filter(
            visa=self.get_visa(),
        ).order_by(
            "display_order",
        )

    def perform_create(self, serializer):
        serializer.save(
            visa=self.get_visa(),
        )


class VisaFAQViewSet(VisaNestedViewSetMixin, ModelViewSet):
    serializer_class = VisaFAQSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_queryset(self):
        return VisaFAQ.objects.filter(
            visa=self.get_visa(),
        ).order_by(
            "display_order",
        )

    def perform_create(self, serializer):
        serializer.save(
            visa=self.get_visa(),
        )


class VisaSEOViewSet(VisaNestedViewSetMixin, ModelViewSet):
    serializer_class = VisaSEOSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_queryset(self):
        return VisaSEO.objects.filter(
            visa=self.get_visa(),
        )

    def perform_create(self, serializer):
        serializer.save(
            visa=self.get_visa(),
        )


class VisaJobViewSet(VisaNestedViewSetMixin, ModelViewSet):
    serializer_class = VisaJobSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
    DjangoFilterBackend,
    SearchFilter,
    OrderingFilter,
]

    filterset_class = VisaJobFilter

    search_fields = [
        "title",
    ]

    ordering_fields = [
        "minimum_salary",
        "maximum_salary",
        "vacancies",
        "created_at",
    ]

    ordering = [
        "display_order",
        "title",
    ]

    def get_queryset(self):
        return VisaJob.objects.filter(
            visa=self.get_visa(),
        ).prefetch_related(
            "facilities",
        )

    def perform_create(self, serializer):
        serializer.save(
            visa=self.get_visa(),
        )


class JobFacilityViewSet(ModelViewSet):
    serializer_class = JobFacilitySerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_queryset(self):
        return JobFacility.objects.filter(
            job_id=self.kwargs.get("job_pk"),
        )

    def perform_create(self, serializer):
        serializer.save(
            job_id=self.kwargs.get("job_pk"),
        )