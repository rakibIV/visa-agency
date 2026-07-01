
# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404
from rest_framework.filters import (
    OrderingFilter,
    SearchFilter,
)
from rest_framework.viewsets import ModelViewSet
from .filters import ApplicantFilter
from .permissions import IsAdminOrReadOnly


from .filters import (
    AgreementTemplateFilter,
    ApplicantTagFilter,
    ApplicationStatusFilter,
    ApplicantPaymentFilter,
    ApplicantDocumentFilter,
    ApplicantNoteFilter,
)
from .models import (
    AgreementTemplate,
    ApplicantTag,
    ApplicationStatus,
)

from .selectors import (
    get_agreement_templates,
    get_applicant_tags,
    get_application_statuses,
    get_addresses,
    get_applicant_detail,
    get_applicant_by_id,
    get_applicants,
    get_documents,
    get_notes,
    get_payments,
    get_status_history,
)

from .serializers import (
    AgreementTemplateSerializer,
    ApplicantTagSerializer,
    ApplicationStatusSerializer,
    ApplicantDetailSerializer,
    ApplicantListSerializer,
    ApplicantSerializer,
    ApplicantAddressSerializer,
    ApplicantPaymentSerializer,
    ApplicantDocumentSerializer,
    ApplicantNoteSerializer,
    ApplicantStatusHistorySerializer,
)


# ==========================================================
# Application Status
# ==========================================================

class ApplicationStatusViewSet(ModelViewSet):

    queryset = get_application_statuses()

    serializer_class = ApplicationStatusSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ApplicationStatusFilter

    search_fields = [
        "name",
        "slug",
        "description",
    ]

    ordering_fields = [
        "display_order",
        "name",
        "created_at",
    ]

    ordering = [
        "display_order",
        "name",
    ]


# ==========================================================
# Applicant Tag
# ==========================================================

class ApplicantTagViewSet(ModelViewSet):

    queryset = get_applicant_tags()

    serializer_class = ApplicantTagSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ApplicantTagFilter

    search_fields = [
        "name",
    ]

    ordering_fields = [
        "name",
        "created_at",
    ]

    ordering = [
        "name",
    ]


# ==========================================================
# Agreement Template
# ==========================================================

class AgreementTemplateViewSet(ModelViewSet):

    queryset = get_agreement_templates()

    serializer_class = AgreementTemplateSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = AgreementTemplateFilter

    search_fields = [
        "title",
        "body",
    ]

    ordering_fields = [
        "title",
        "version",
        "created_at",
    ]

    ordering = [
        "title",
    ]


# ==========================================================
# Applicant
# ==========================================================

class ApplicantViewSet(ModelViewSet):

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ApplicantFilter

    search_fields = [
        "application_id",
        "full_name",
        "passport_number",
        "nid_number",
        "profile__phone",
        "profile__email",
    ]

    ordering_fields = [
        "application_id",
        "full_name",
        "created_at",
        "date_of_birth",
    ]

    ordering = [
        "-created_at",
    ]

    def get_queryset(self):

        if self.action == "retrieve":
            applicant = get_applicant_detail(
                self.kwargs["pk"],
            )

            if applicant is None:
                return get_applicants().none()

            return get_applicants().filter(
                pk=applicant.pk,
            )

        return get_applicants()

    def get_serializer_class(self):

        if self.action == "list":
            return ApplicantListSerializer

        if self.action == "retrieve":
            return ApplicantDetailSerializer

        return ApplicantSerializer

    def perform_create(
        self,
        serializer,
    ):

        serializer.save(
            created_by=self.request.user
            if self.request.user.is_authenticated
            else None,
            updated_by=self.request.user
            if self.request.user.is_authenticated
            else None,
        )

    def perform_update(
        self,
        serializer,
    ):

        serializer.save(
            updated_by=self.request.user
            if self.request.user.is_authenticated
            else None,
        )



# ==========================================================
# Applicant Address
# ==========================================================

class ApplicantNestedViewSetMixin:

    def get_applicant(self):

        applicant = get_applicant_by_id(
            self.kwargs["applicant_pk"],
        )

        if applicant is None:
            raise Http404

        return applicant


class ApplicantAddressViewSet(ApplicantNestedViewSetMixin, ModelViewSet):

    serializer_class = ApplicantAddressSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    

    def get_queryset(self):

        return get_addresses(
            self.get_applicant(),
        )

    def perform_create(self, serializer):

        serializer.save(
            applicant=self.get_applicant(),
        )


# ==========================================================
# Applicant Payment
# ==========================================================

class ApplicantPaymentViewSet(ApplicantNestedViewSetMixin, ModelViewSet):

    serializer_class = ApplicantPaymentSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = ApplicantPaymentFilter

    ordering_fields = [
        "payment_number",
        "payment_date",
        "created_at",
    ]

    ordering = [
        "-payment_date",
    ]

    def get_queryset(self):

        return get_payments(
            self.get_applicant(),
        )

    def perform_create(self, serializer):

        serializer.save(
            applicant=self.get_applicant(),
        )



# ==========================================================
# Applicant Document
# ==========================================================

class ApplicantDocumentViewSet(ApplicantNestedViewSetMixin, ModelViewSet):

    serializer_class = ApplicantDocumentSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = ApplicantDocumentFilter

    ordering_fields = [
        "document_type",
        "created_at",
    ]

    ordering = [
        "document_type",
    ]

    def get_queryset(self):

        return get_documents(
            self.get_applicant(),
        )

    def perform_create(self, serializer):

        serializer.save(
            applicant=self.get_applicant(),
        )


# ==========================================================
# Applicant Note
# ==========================================================

class ApplicantNoteViewSet(ApplicantNestedViewSetMixin, ModelViewSet):

    serializer_class = ApplicantNoteSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = ApplicantNoteFilter

    ordering_fields = [
        "created_at",
    ]

    ordering = [
        "-created_at",
    ]

    def get_queryset(self):

        return get_notes(
            self.get_applicant(),
        )

    def perform_create(self, serializer):

        serializer.save(
            applicant=self.get_applicant(),
        )


# ==========================================================
# Applicant Status History
# ==========================================================

class ApplicantStatusHistoryViewSet(ApplicantNestedViewSetMixin, ModelViewSet):

    serializer_class = ApplicantStatusHistorySerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    http_method_names = [
        "get",
        "head",
        "options",
    ]

    filter_backends = [
        OrderingFilter,
    ]

    ordering_fields = [
        "created_at",
    ]

    ordering = [
        "-created_at",
    ]

    def get_queryset(self):

        return get_status_history(
            self.get_applicant(),
        )
