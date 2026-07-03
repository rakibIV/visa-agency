from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from .filters import AgencyServiceFilter
from .models import (
    AgencyService,
    CompanyInformation,
    Office,
    SocialLink,
    EmailTemplate,
    Lawyer,
)
from .permissions import IsAdminOrReadOnly
from .serializers import (
    AgencyServiceSerializer,
    CompanyInformationSerializer,
    CompanyInformationDetailSerializer,
    OfficeSerializer,
    SocialLinkSerializer,
    EmailTemplateSerializer,
    LawyerSerializer,
)


class AgencyServiceViewSet(ModelViewSet):
    queryset = AgencyService.objects.all()

    serializer_class = AgencyServiceSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = AgencyServiceFilter

    search_fields = [
        "title",
    ]

    ordering_fields = [
        "title",
        "display_order",
        "created_at",
    ]

    ordering = [
        "display_order",
        "title",
    ]


class CompanyInformationViewSet(ModelViewSet):
    queryset = CompanyInformation.objects.all()

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CompanyInformationDetailSerializer

        return CompanyInformationSerializer


class OfficeViewSet(ModelViewSet):
    queryset = Office.objects.all()

    serializer_class = OfficeSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        OrderingFilter,
        SearchFilter,
    ]

    search_fields = [
        "branch_name",
        "address",
    ]

    ordering_fields = [
        "display_order",
        "branch_name",
    ]

    ordering = [
        "display_order",
        "branch_name",
    ]


class SocialLinkViewSet(ModelViewSet):
    queryset = SocialLink.objects.all()

    serializer_class = SocialLinkSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    ordering = [
        "display_order",
    ]


class EmailTemplateViewSet(ModelViewSet):
    serializer_class = EmailTemplateSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    def get_queryset(self):
        return (
            EmailTemplate.objects.select_related(
                "status",
            )
            .order_by(
                "name",
            )
        )

    search_fields = [
        "name",
        "subject",
        "body",
        "status__name",
    ]

    ordering_fields = [
        "name",
        "status",
        "created_at",
    ]

    ordering = [
        "name",
    ]


class LawyerViewSet(ModelViewSet):
    serializer_class = LawyerSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    def get_queryset(self):
        return (
            Lawyer.objects.select_related(
                "country",
            )
            .order_by(
                "-is_default",
                "name",
            )
        )

    search_fields = [
        "name",
        "email",
        "env_key",
        "phone",
        "country__name",
    ]

    ordering_fields = [
        "name",
        "is_default",
        "created_at",
    ]

    ordering = [
        "-is_default",
        "name",
    ]
