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

    in_progress = django_filters.BooleanFilter(
        method="filter_in_progress"
    )

    is_approved = django_filters.BooleanFilter(
        method="filter_is_approved"
    )

    status_name = django_filters.CharFilter(
        method="filter_status_name"
    )

    def filter_in_progress(self, queryset, name, value):
        if value:
            from applicant.selectors import get_approved_status_ids, get_rejected_status_ids
            approved_ids = get_approved_status_ids()
            rejected_ids = get_rejected_status_ids()
            return queryset.exclude(status_id__in=approved_ids + rejected_ids)
        return queryset

    def filter_is_approved(self, queryset, name, value):
        from applicant.selectors import get_approved_status_ids
        approved_ids = get_approved_status_ids()
        if value:
            return queryset.filter(status_id__in=approved_ids)
        return queryset.exclude(status_id__in=approved_ids)

    def filter_status_name(self, queryset, name, value):
        if not value:
            return queryset
        val_lower = value.strip().lower()
        if val_lower in ["approve", "approved", "visa approved", "visa_approved"]:
            from applicant.selectors import get_approved_status_ids
            return queryset.filter(status_id__in=get_approved_status_ids())
        if val_lower in ["reject", "rejected", "visa rejected", "visa_rejected"]:
            from applicant.selectors import get_rejected_status_ids
            return queryset.filter(status_id__in=get_rejected_status_ids())
        return queryset.filter(status__name__icontains=value)

    email = django_filters.CharFilter(
        field_name="profile__email",
        lookup_expr="icontains",
    )

    phone = django_filters.CharFilter(
        field_name="profile__phone",
        lookup_expr="icontains",
    )

    search = django_filters.CharFilter(
        method="filter_search"
    )

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        val = value.strip()
        from django.db.models import Q
        return queryset.filter(
            Q(full_name__icontains=val) |
            Q(application_id__icontains=val) |
            Q(passport_number__icontains=val) |
            Q(nid_number__icontains=val) |
            Q(profile__email__icontains=val) |
            Q(profile__phone__icontains=val) |
            Q(profile__emergency_contact_phone__icontains=val)
        ).distinct()

    class Meta:
        model = Applicant

        fields = {
            "application_id": ["exact", "icontains"],
            "full_name": ["icontains"],
            "passport_number": ["exact", "icontains"],
            "nid_number": ["exact", "icontains"],
            "visa": ["exact"],
            "status": ["exact"],
            "status__name": ["exact", "icontains"],
            "status__slug": ["exact", "icontains"],
            "slot": ["exact"],
            "agreement": ["exact"],
            "current_country": ["icontains"],
            "created_at": ["date"],
            "profile__email": ["exact", "icontains"],
            "profile__phone": ["exact", "icontains"],
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



