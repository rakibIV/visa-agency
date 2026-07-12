
# Create your views here.
from typing import Any, cast

from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import (
    OrderingFilter,
    SearchFilter,
)
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet
from .filters import ApplicantFilter
from .permissions import IsAdminOrReadOnly
from django.shortcuts import render
from core.choices import PaymentMethod

from .filters import (
    AgreementTemplateFilter,
    ApplicantTagFilter,
    ApplicationStatusFilter,
    ApplicantPaymentFilter,
    ApplicantMoneyReceiptFilter,
    ApplicantRefundFilter,
    ApplicantRefundReceiptFilter,
    ApplicantDocumentFilter,
    ApplicantNoteFilter,
)
from .models import (
    AgreementTemplate,
    AgreementTemplateClause,
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
    get_money_receipts,
    get_notes,
    get_payments,
    get_refund_bank_detail,
    get_refunds,
    get_refund_receipts,
    get_status_history,
)

from .serializers import (
    AgreementTemplateClauseSerializer,
    AgreementTemplateSerializer,
    ApplicantTagSerializer,
    ApplicationStatusSerializer,
    ApplicantDetailSerializer,
    ApplicantListSerializer,
    ApplicantSerializer,
    ApplicantAddressSerializer,
    ApplicantPaymentSerializer,
    ApplicantMoneyReceiptSerializer,
    ApplicantRefundBankDetailSerializer,
    ApplicantRefundSerializer,
    ApplicantRefundSummarySerializer,
    ApplicantRefundReceiptSerializer,
    GenerateMoneyReceiptSerializer,
    GenerateRefundSerializer,
    GenerateRefundReceiptSerializer,
    ApplicantDocumentSerializer,
    ApplicantNoteSerializer,
    ApplicantStatusHistorySerializer,
    ApplicantStatusEmailUpdateSerializer,
    ApplicantManualEmailSerializer,
    MailTriggerSerializer,
)
from .services import (
    change_applicant_status,
    send_manual_applicant_email,
)
from .emailing import (
    get_staff_display_name,
    send_applicant_email,
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


class AgreementTemplateClauseViewSet(ModelViewSet):

    queryset = AgreementTemplateClause.objects.select_related("template").prefetch_related("countries")

    serializer_class = AgreementTemplateClauseSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "title_en",
        "title_ar",
        "title_bn",
        "body_en",
        "body_ar",
        "body_bn",
    ]

    ordering_fields = [
        "clause_number",
        "created_at",
    ]

    ordering = [
        "template",
        "clause_number",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        template_id = self.kwargs.get("template_pk")

        if template_id is not None:
            queryset = queryset.filter(template_id=template_id)

        return queryset





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

    def get_queryset(self):  # type: ignore[override]

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

    def get_serializer_class(self):  # type: ignore[override]

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

    @action(
        detail=False,
        methods=[
            "post",
        ],
        url_path="trigger-send",
    )
    def trigger_send(self, request):
        serializer = MailTriggerSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        validated_data = cast(
            dict[str, Any],
            getattr(serializer, "validated_data", {}) or {},
        )
        applicant = validated_data["applicant"]
        template = validated_data["template"]
        sender = validated_data["sender"]

        try:
            result = send_applicant_email(
                applicant=applicant,
                sender=sender,
                template=template,
                staff_name=get_staff_display_name(
                    request.user if request.user.is_authenticated else None
                ),
            )
        except ValidationError as exc:
            return Response(
                {
                    "detail": "Email dispatch failed.",
                    "error": exc.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            return Response(
                {
                    "detail": "Email dispatch failed.",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "detail": "Email sent successfully.",
                "data": result,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=[
            "patch",
        ],
        url_path="change-status",
    )
    def change_status(self, request, pk=None):
        applicant = get_applicant_detail(pk)

        if applicant is None:
            raise Http404

        serializer = ApplicantStatusEmailUpdateSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        validated_data = cast(
            dict[str, Any],
            getattr(serializer, "validated_data", {}) or {},
        )

        changed_by = getattr(
            request.user,
            "staff_profile",
            None,
        ) if request.user.is_authenticated else None

        change_applicant_status(
            applicant=applicant,
            new_status=validated_data["status"],
            changed_by=changed_by,
            updated_by=request.user if request.user.is_authenticated else None,
            remarks=validated_data.get(
                "remarks",
                "",
            ),
            sender=validated_data.get("sender") or applicant.lawyer,
            send_email=True,
        )

        return Response(
            ApplicantDetailSerializer(
                get_applicant_detail(pk),
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=[
            "post",
        ],
        url_path="send-email",
    )
    def send_email(self, request, pk=None):
        applicant = get_applicant_detail(pk)

        if applicant is None:
            raise Http404

        serializer = ApplicantManualEmailSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        validated_data = cast(
            dict[str, Any],
            getattr(serializer, "validated_data", {}) or {},
        )

        send_manual_applicant_email(
            applicant=applicant,
            sender=validated_data["sender"],
            template=validated_data["template"],
            sent_by=request.user if request.user.is_authenticated else None,
        )

        return Response(
            {
                "detail": "Email sent successfully.",
            },
            status=status.HTTP_200_OK,
        )



# ==========================================================
# Applicant Address
# ==========================================================

class ApplicantNestedViewSetMixin:

    def get_applicant(self):

        kwargs = getattr(self, "kwargs", {})
        applicant = get_applicant_by_id(
            kwargs.get("applicant_pk"),
        )

        if applicant is None:
            raise Http404

        return applicant


class ApplicantAddressViewSet(ApplicantNestedViewSetMixin, ModelViewSet):

    serializer_class = ApplicantAddressSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    

    def get_queryset(self):  # type: ignore[override]

        return get_addresses(
            self.get_applicant(),
        )

    def perform_create(self, serializer):

        serializer.save(
            applicant=self.get_applicant(),
            generated_by=self.request.user
            if self.request.user.is_authenticated
            else None,
        )

    @action(
        detail=True,
        methods=[
            "post",
        ],
        url_path="generate-receipt",
    )
    def generate_receipt(self, request, applicant_pk=None, pk=None):
        payment = self.get_object()

        serializer = GenerateMoneyReceiptSerializer(
            data={
                "payment": payment.pk,
                **request.data,
            },
            context={
                "applicant": self.get_applicant(),
                "user": request.user,
            },
        )
        serializer.is_valid(
            raise_exception=True,
        )

        receipt = serializer.save()

        return Response(
            ApplicantMoneyReceiptSerializer(
                receipt,
            ).data,
            status=status.HTTP_201_CREATED,
        )


class ApplicantMoneyReceiptViewSet(ApplicantNestedViewSetMixin, ModelViewSet):

    serializer_class = ApplicantMoneyReceiptSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    http_method_names = [
        "get",
        "head",
        "options",
    ]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = ApplicantMoneyReceiptFilter

    ordering_fields = [
        "receipt_number",
        "payment_date",
        "generated_at",
        "created_at",
    ]

    ordering = [
        "-generated_at",
    ]

    def get_queryset(self):  # type: ignore[override]

        return get_money_receipts(
            self.get_applicant(),
        )


class ApplicantRefundBankDetailViewSet(ApplicantNestedViewSetMixin, ModelViewSet):

    serializer_class = ApplicantRefundBankDetailSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "head",
        "options",
    ]

    def get_queryset(self):  # type: ignore[override]

        bank_detail = get_refund_bank_detail(
            self.get_applicant(),
        )

        if bank_detail is None:
            return self.serializer_class.Meta.model.objects.none()

        return self.serializer_class.Meta.model.objects.filter(
            pk=bank_detail.pk,
        )

    def list(self, request, *args, **kwargs):
        bank_detail = get_refund_bank_detail(
            self.get_applicant(),
        )

        if bank_detail is None:
            return Response(
                None,
                status=status.HTTP_200_OK,
            )

        return Response(
            self.get_serializer(
                bank_detail,
            ).data,
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        bank_detail = get_refund_bank_detail(
            self.get_applicant(),
        )
        serializer = self.get_serializer(
            bank_detail,
            data=request.data,
            partial=bank_detail is not None,
        )
        serializer.is_valid(
            raise_exception=True,
        )
        serializer.save(
            applicant=self.get_applicant(),
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
            if bank_detail
            else status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):

        serializer.save(
            applicant=self.get_applicant(),
        )


class ApplicantRefundViewSet(ApplicantNestedViewSetMixin, ModelViewSet):

    serializer_class = ApplicantRefundSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    http_method_names = [
        "get",
        "post",
        "head",
        "options",
    ]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = ApplicantRefundFilter

    ordering_fields = [
        "refund_date",
        "refund_amount",
        "created_at",
    ]

    ordering = [
        "-refund_date",
    ]

    def get_queryset(self):  # type: ignore[override]

        return get_refunds(
            self.get_applicant(),
        )

    def create(self, request, *args, **kwargs):
        serializer = GenerateRefundSerializer(
            data=request.data,
            context={
                "applicant": self.get_applicant(),
                "user": request.user,
            },
        )
        serializer.is_valid(
            raise_exception=True,
        )

        refund = serializer.save()

        if refund is None:
            return Response(
                {
                    "detail": "No refundable payment total is available."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            self.get_serializer(
                refund,
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=[
            "get",
        ],
        url_path="summary",
    )
    def summary(self, request, applicant_pk=None):
        return Response(
            ApplicantRefundSummarySerializer(
                self.get_applicant(),
            ).data,
            status=status.HTTP_200_OK,
        )


class ApplicantRefundReceiptViewSet(ApplicantNestedViewSetMixin, ModelViewSet):

    serializer_class = ApplicantRefundReceiptSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    http_method_names = [
        "get",
        "post",
        "head",
        "options",
    ]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = ApplicantRefundReceiptFilter

    ordering_fields = [
        "receipt_number",
        "generated_at",
        "created_at",
    ]

    ordering = [
        "-generated_at",
    ]

    def get_queryset(self):  # type: ignore[override]

        return get_refund_receipts(
            self.get_applicant(),
        )

    def create(self, request, *args, **kwargs):
        serializer = GenerateRefundReceiptSerializer(
            data=request.data,
            context={
                "applicant": self.get_applicant(),
                "user": request.user,
            },
        )
        serializer.is_valid(
            raise_exception=True,
        )

        receipt = serializer.save()

        return Response(
            self.get_serializer(
                receipt,
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="print")
    def print_receipt(self, request, applicant_pk=None, pk=None):
        
        
        receipt = self.get_object()
        applicant = receipt.applicant
        
        context = {
            "receipt": receipt,
            "applicant": applicant,
            "profile": getattr(applicant, "profile", None),
        }
        
        if receipt.refund_method == PaymentMethod.CHEQUE:
            template_name = "applicant/receipts/cheque_receipt.html"
        elif receipt.refund_method == PaymentMethod.BANK:
            template_name = "applicant/receipts/bank_receipt.html"
        else:
            template_name = "applicant/receipts/cash_receipt.html"
            
        return render(request, template_name, context)


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

    def get_queryset(self):  # type: ignore[override]

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

    def get_queryset(self):  # type: ignore[override]

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

    def get_queryset(self):  # type: ignore[override]

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

    def get_queryset(self):  # type: ignore[override]

        return get_status_history(
            self.get_applicant(),
        )
