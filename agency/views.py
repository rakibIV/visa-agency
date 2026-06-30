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
)
from .permissions import IsAdminOrReadOnly
from .serializers import (
    AgencyServiceSerializer,
    CompanyInformationSerializer,
    CompanyInformationDetailSerializer,
    OfficeSerializer,
    SocialLinkSerializer,
    EmailTemplateSerializer,
)


class AgencyServiceViewSet(ModelViewSet):
    queryset = AgencyService.objects.filter(
        is_active=True,
    )

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
    queryset = CompanyInformation.objects.filter(
        is_active=True,
    )

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CompanyInformationDetailSerializer

        return CompanyInformationSerializer


class OfficeViewSet(ModelViewSet):
    queryset = Office.objects.filter(
        is_active=True,
    )

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
    queryset = SocialLink.objects.filter(
        is_active=True,
    )

    serializer_class = SocialLinkSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    ordering = [
        "display_order",
    ]


class EmailTemplateViewSet(ModelViewSet):
    queryset = EmailTemplate.objects.filter(
        is_active=True,
    )

    serializer_class = EmailTemplateSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    search_fields = [
        "name",
        "subject",
    ]

    ordering_fields = [
        "name",
        "created_at",
    ]

    ordering = [
        "name",
    ]