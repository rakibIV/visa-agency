from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
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


class VisaRequirementViewSet(ModelViewSet):
    serializer_class = VisaRequirementSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_queryset(self):
        return VisaRequirement.objects.filter(
            visa_id=self.kwargs.get("visa_pk"),
        ).order_by(
            "display_order",
            "title",
        )

    def perform_create(self, serializer):
        serializer.save(
            visa_id=self.kwargs.get("visa_pk"),
        )


class VisaStepViewSet(ModelViewSet):
    serializer_class = VisaStepSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_queryset(self):
        return VisaStep.objects.filter(
            visa_id=self.kwargs.get("visa_pk"),
        ).order_by(
            "display_order",
        )

    def perform_create(self, serializer):
        serializer.save(
            visa_id=self.kwargs.get("visa_pk"),
        )


class VisaFAQViewSet(ModelViewSet):
    serializer_class = VisaFAQSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_queryset(self):
        return VisaFAQ.objects.filter(
            visa_id=self.kwargs.get("visa_pk"),
        ).order_by(
            "display_order",
        )

    def perform_create(self, serializer):
        serializer.save(
            visa_id=self.kwargs.get("visa_pk"),
        )


class VisaSEOViewSet(ModelViewSet):
    serializer_class = VisaSEOSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_queryset(self):
        return VisaSEO.objects.filter(
            visa_id=self.kwargs.get("visa_pk"),
        )

    def perform_create(self, serializer):
        serializer.save(
            visa_id=self.kwargs.get("visa_pk"),
        )


class VisaJobViewSet(ModelViewSet):
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
            visa_id=self.kwargs.get("visa_pk"),
        ).prefetch_related(
            "facilities",
        )

    def perform_create(self, serializer):
        serializer.save(
            visa_id=self.kwargs.get("visa_pk"),
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