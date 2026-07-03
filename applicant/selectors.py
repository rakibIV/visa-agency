from django.db.models import Count, Prefetch, Q, Sum

from .models import (
    Applicant,
    ApplicantAddress,
    ApplicantDocument,
    ApplicantNote,
    ApplicantPayment,
    ApplicantProfile,
    ApplicantStatusHistory,
    ApplicationStatus,
    ApplicantTag,
    AgreementTemplate,
    CurrencyRate,
)


# =========================================================
# Lookup Selectors
# =========================================================

def get_application_statuses():
    return (
        ApplicationStatus.objects.filter(
            is_active=True,
        )
        .order_by(
            "display_order",
            "name",
        )
    )


def get_default_application_status():
    return (
        ApplicationStatus.objects.filter(
            is_default=True,
            is_active=True,
        )
        .first()
    )


def get_applicant_tags():
    return ApplicantTag.objects.order_by(
        "name",
    )


def get_agreement_templates():
    return (
        AgreementTemplate.objects.filter(
            is_active=True,
        )
        .select_related(
            "visa",
        )
        .order_by(
            "title",
        )
    )


def get_currency_rates():
    return (
        CurrencyRate.objects.all()
        .order_by(
            "-fetched_at",
            "base_currency",
            "target_currency",
        )
    )


# =========================================================
# Applicant Selectors
# =========================================================

def get_applicants():
    return (
        Applicant.objects.filter(
            is_deleted=False,
        )
        .select_related(
            "visa",
            "job",
            "status",
            "slot",
            "slot__staff",
            "agreement",
        )
        .prefetch_related(
            "tags",
        )
        .order_by(
            "-created_at",
        )
    )


def get_applicant_by_id(pk):
    return (
        get_applicants()
        .filter(
            pk=pk,
        )
        .first()
    )


def get_applicant_by_application_id(application_id):
    return (
        get_applicants()
        .filter(
            application_id=application_id,
        )
        .first()
    )


def get_applicant_by_passport(passport_number):
    return (
        get_applicants()
        .filter(
            passport_number=passport_number,
        )
        .first()
    )


def get_applicant_detail(pk):
    return (
        Applicant.objects.filter(
            pk=pk,
            is_deleted=False,
        )
        .select_related(
            "visa",
            "job",
            "status",
            "slot",
            "slot__staff",
            "agreement",
            "profile",
        )
        .prefetch_related(
            "tags",
            "addresses",
            "payments",
            "documents",
            "notes",
            "status_history",
        )
        .first()
    )


# =========================================================
# Applicant Profile
# =========================================================

def get_profile(applicant):
    return (
        ApplicantProfile.objects.select_related(
            "applicant",
        )
        .filter(
            applicant=applicant,
        )
        .first()
    )


# =========================================================
# Applicant Address
# =========================================================

def get_addresses(applicant):
    return (
        ApplicantAddress.objects.filter(
            applicant=applicant,
        )
        .select_related(
            "country",
        )
        .order_by(
            "address_type",
        )
    )


# =========================================================
# Applicant Payments
# =========================================================

def get_payments(applicant):
    return (
        ApplicantPayment.objects.filter(
            applicant=applicant,
        )
        .select_related(
            "received_by",
        )
        .order_by(
            "payment_number",
        )
    )


def get_total_paid(applicant):
    return (
        ApplicantPayment.objects.filter(
            applicant=applicant,
        ).aggregate(
            total=Sum(
                "euro_amount",
            )
        )["total"]
        or 0
    )


# =========================================================
# Applicant Documents
# =========================================================

def get_documents(applicant):
    return (
        ApplicantDocument.objects.filter(
            applicant=applicant,
        )
        .select_related(
            "verified_by",
        )
        .order_by(
            "document_type",
        )
    )


def get_verified_documents(applicant):
    return (
        get_documents(
            applicant,
        ).filter(
            verified=True,
        )
    )


# =========================================================
# Applicant Notes
# =========================================================

def get_notes(applicant):
    return (
        ApplicantNote.objects.filter(
            applicant=applicant,
        )
        .select_related(
            "staff",
        )
        .order_by(
            "-created_at",
        )
    )


# =========================================================
# Status History
# =========================================================

def get_status_history(applicant):
    return (
        ApplicantStatusHistory.objects.filter(
            applicant=applicant,
        )
        .select_related(
            "old_status",
            "new_status",
            "changed_by",
        )
        .order_by(
            "-created_at",
        )
    )


# =========================================================
# Dashboard / Statistics
# =========================================================

def get_applicant_statistics():
    queryset = Applicant.objects.filter(
        is_deleted=False,
    )

    return {
        "total": queryset.count(),
        "approved": queryset.filter(
            status__slug="approved",
        ).count(),
        "rejected": queryset.filter(
            status__slug="rejected",
        ).count(),
        "processing": queryset.exclude(
            status__slug__in=[
                "approved",
                "rejected",
            ]
        ).count(),
    }


def get_staff_statistics(staff):
    queryset = Applicant.objects.filter(
        slot__staff=staff,
        is_deleted=False,
    )

    return {
        "total": queryset.count(),
        "approved": queryset.filter(
            status__slug="approved",
        ).count(),
        "rejected": queryset.filter(
            status__slug="rejected",
        ).count(),
        "processing": queryset.exclude(
            status__slug__in=[
                "approved",
                "rejected",
            ]
        ).count(),
    }


# =========================================================
# Search
# =========================================================

def search_applicants(keyword):
    return (
        get_applicants()
        .filter(
            Q(
                application_id__icontains=keyword,
            )
            | Q(
                full_name__icontains=keyword,
            )
            | Q(
                passport_number__icontains=keyword,
            )
            | Q(
                profile__phone__icontains=keyword,
            )
            | Q(
                profile__email__icontains=keyword,
            )
        )
        .distinct()
    )
