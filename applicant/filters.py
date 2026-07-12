import django_filters

from .models import (
    AgreementTemplate,
    Applicant,
    ApplicantDocument,
    ApplicantMoneyReceipt,
    ApplicantNote,
    ApplicantPayment,
    ApplicantRefund,
    ApplicantRefundReceipt,
    ApplicantTag,
    ApplicationStatus,
)


# ==========================================================
# Application Status
# ==========================================================

class ApplicationStatusFilter(django_filters.FilterSet):

    class Meta:
        model = ApplicationStatus

        fields = {
            "is_default": ["exact"],
            "is_final": ["exact"],
            "is_active": ["exact"],
        }


# ==========================================================
# Applicant Tag
# ==========================================================

class ApplicantTagFilter(django_filters.FilterSet):

    class Meta:
        model = ApplicantTag

        fields = {
            "name": ["icontains"],
        }


# ==========================================================
# Agreement Template
# ==========================================================

class AgreementTemplateFilter(django_filters.FilterSet):

    class Meta:
        model = AgreementTemplate

        fields = {
            "is_active": ["exact"],
            "version": ["exact"],
        }


# ==========================================================
# Applicant
# ==========================================================

class ApplicantFilter(django_filters.FilterSet):

    created_from = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__gte",
    )

    created_to = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__lte",
    )

    dob_from = django_filters.DateFilter(
        field_name="date_of_birth",
        lookup_expr="gte",
    )

    dob_to = django_filters.DateFilter(
        field_name="date_of_birth",
        lookup_expr="lte",
    )

    class Meta:
        model = Applicant

        fields = {
            "application_id": ["exact", "icontains"],
            "full_name": ["icontains"],
            "passport_number": ["exact", "icontains"],
            "nid_number": ["exact", "icontains"],
            "visa": ["exact"],
            "status": ["exact"],
            "slot": ["exact"],
            "agreement": ["exact"],
            "current_country": ["icontains"],
            "created_at": ["date"],
        }


# ==========================================================
# Applicant Payment
# ==========================================================

class ApplicantPaymentFilter(django_filters.FilterSet):

    payment_from = django_filters.DateFilter(
        field_name="payment_date",
        lookup_expr="gte",
    )

    payment_to = django_filters.DateFilter(
        field_name="payment_date",
        lookup_expr="lte",
    )

    min_amount = django_filters.NumberFilter(
        field_name="amount",
        lookup_expr="gte",
    )

    max_amount = django_filters.NumberFilter(
        field_name="amount",
        lookup_expr="lte",
    )

    class Meta:
        model = ApplicantPayment

        fields = {
            "applicant": ["exact"],
            "payment_method": ["exact"],
            "currency": ["exact"],
            "installment_type": ["exact"],
            "received_by": ["exact"],
        }


class ApplicantMoneyReceiptFilter(django_filters.FilterSet):

    class Meta:
        model = ApplicantMoneyReceipt

        fields = {
            "applicant": ["exact"],
            "payment": ["exact"],
            "receipt_number": ["exact", "icontains"],
            "installment_type": ["exact"],
            "is_active": ["exact"],
            "is_void": ["exact"],
        }


class ApplicantRefundFilter(django_filters.FilterSet):

    class Meta:
        model = ApplicantRefund

        fields = {
            "applicant": ["exact"],
            "refund_status": ["exact"],
            "generated_from_rejection": ["exact"],
            "refund_date": ["exact"],
        }


class ApplicantRefundReceiptFilter(django_filters.FilterSet):

    class Meta:
        model = ApplicantRefundReceipt

        fields = {
            "applicant": ["exact"],
            "refund": ["exact"],
            "receipt_number": ["exact", "icontains"],
            "is_active": ["exact"],
            "is_void": ["exact"],
        }


# ==========================================================
# Applicant Document
# ==========================================================

class ApplicantDocumentFilter(django_filters.FilterSet):

    class Meta:
        model = ApplicantDocument

        fields = {
            "applicant": ["exact"],
            "document_type": ["exact"],
            "verified": ["exact"],
            "verified_by": ["exact"],
        }


# ==========================================================
# Applicant Note
# ==========================================================

class ApplicantNoteFilter(django_filters.FilterSet):

    class Meta:
        model = ApplicantNote

        fields = {
            "applicant": ["exact"],
            "staff": ["exact"],
            "is_private": ["exact"],
        }



