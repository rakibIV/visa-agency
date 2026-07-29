from django.db.models import Count, Max, Prefetch, Q, Sum, F
from django.utils import timezone

from .models import (
    Applicant,
    ApplicantAddress,
    ApplicantDocument,
    ApplicantMoneyReceipt,
    ApplicantNote,
    ApplicantPayment,
    ApplicantProfile,
    ApplicantRefund,
    ApplicantRefundBankDetail,
    ApplicantRefundReceipt,
    ApplicantStatusHistory,
    ApplicationStatus,
    ApplicantTag,
    AgreementTemplate,
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
        .order_by(
            "title",
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
            "slot__staff__user",
            "agreement",
        )
        .prefetch_related(
            "tags",
        )
        .order_by(
            "-created_at",
        )
    )


def get_deleted_applicants():
    return (
        Applicant.objects.filter(
            is_deleted=True,
        )
        .select_related(
            "visa",
            "job",
            "status",
            "slot",
            "slot__staff",
            "slot__staff__user",
            "agreement",
        )
        .prefetch_related(
            "tags",
        )
        .order_by(
            "-deleted_at",
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
            application_id=application_id.upper(),
        )
        .first()
    )


def get_public_applicant_status(
    *,
    application_id,
    email,
    phone,
):
    app_id = application_id.strip()
    clean_email = email.strip()
    clean_phone = phone.strip()
    phone_digits = "".join(filter(str.isdigit, clean_phone))

    queryset = (
        Applicant.objects.filter(is_deleted=False)
        .select_related(
            "visa",
            "visa__country",
            "job",
            "secondary_job",
            "status",
            "profile",
            "slot",
            "slot__staff",
            "slot__staff__user",
            "slot__staff__designation",
        )
        .prefetch_related(
            "status_history__new_status",
            "payments",
            "refunds",
        )
    )

    # 1. Direct match on app_id, email (case-insensitive), and phone
    applicant = queryset.filter(
        application_id__iexact=app_id,
        profile__email__iexact=clean_email,
        profile__phone=clean_phone,
    ).first()

    if applicant:
        return applicant

    # 2. Flexible match handling phone formatting variations (e.g. +880 vs 0)
    if phone_digits:
        phone_suffix = phone_digits[-10:] if len(phone_digits) >= 10 else phone_digits
        applicant = queryset.filter(
            application_id__iexact=app_id,
            profile__email__iexact=clean_email,
            profile__phone__icontains=phone_suffix,
        ).first()

        if applicant:
            return applicant

    # 3. Fallback match on app_id and email
    return queryset.filter(
        application_id__iexact=app_id,
        profile__email__iexact=clean_email,
    ).first()


def get_status_classification():
    """
    Returns a dict containing 'approved_ids' and 'rejected_ids' in a single query pass.
    """
    statuses = list(ApplicationStatus.objects.filter(is_active=True).order_by("display_order", "id"))
    
    visa_app_st = next(
        (s for s in statuses if "visa approved" in (s.name or "").lower() or "visa-approved" in (s.slug or "").lower()),
        None
    )
    if not visa_app_st:
        visa_app_st = next(
            (s for s in statuses if (s.name or "").lower() == "approved" or (s.slug or "").lower() == "approved"),
            None
        )
    if not visa_app_st:
        visa_app_st = next(
            (s for s in statuses if "approve" in (s.name or "").lower() or "approve" in (s.slug or "").lower()),
            None
        )

    approved_start_order = visa_app_st.display_order if visa_app_st else 999999

    approved_ids = []
    rejected_ids = []

    for st in statuses:
        name_lower = (st.name or "").lower()
        slug_lower = (st.slug or "").lower()
        is_reject = any(k in name_lower or k in slug_lower for k in ["reject", "cancel", "refuse"])

        if is_reject:
            rejected_ids.append(st.id)
        elif st.display_order >= approved_start_order:
            approved_ids.append(st.id)

    return {
        "approved_ids": approved_ids,
        "rejected_ids": rejected_ids,
    }


def get_approved_status_ids():
    return get_status_classification()["approved_ids"]


def get_rejected_status_ids():
    return get_status_classification()["rejected_ids"]


def get_public_current_month_applicant_results():
    today = timezone.localdate()
    start_date = today - timezone.timedelta(days=90)
    approved_ids = get_approved_status_ids()
    rejected_ids = get_rejected_status_ids()
    relevant_status_ids = approved_ids + rejected_ids

    return (
        Applicant.objects.filter(
            is_deleted=False,
            status_id__in=relevant_status_ids,
            updated_at__date__gte=start_date,
            updated_at__date__lte=today,
        )
        .select_related(
            "visa",
            "visa__country",
            "job",
            "status",
        )
        .annotate(
            result_date=F("updated_at")
        )
        .order_by(
            "-result_date",
            "application_id",
        )
        .distinct()
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
            "visa__country",
            "job",
            "secondary_job",
            "status",
            "slot",
            "slot__staff",
            "slot__staff__user",
            "agreement",
            "profile",
            "refund_bank_detail",
        )
        .prefetch_related(
            "tags",
            "addresses",
            Prefetch("payments", queryset=ApplicantPayment.objects.select_related("received_by", "received_by__user")),
            Prefetch("money_receipts", queryset=ApplicantMoneyReceipt.objects.select_related("payment", "generated_by")),
            "refunds",
            "refund_receipts",
            Prefetch("documents", queryset=ApplicantDocument.objects.select_related("verified_by", "verified_by__user")),
            Prefetch("notes", queryset=ApplicantNote.objects.select_related("staff", "staff__user")),
            Prefetch("status_history", queryset=ApplicantStatusHistory.objects.select_related(
                "old_status", "new_status", "changed_by", "changed_by__user"
            )),
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


def get_money_receipts(applicant):
    return (
        ApplicantMoneyReceipt.objects.filter(
            applicant=applicant,
        )
        .select_related(
            "payment",
            "generated_by",
        )
        .order_by(
            "-generated_at",
        )
    )


def get_refund_bank_detail(applicant):
    return (
        ApplicantRefundBankDetail.objects.filter(
            applicant=applicant,
        ).first()
    )


def get_refunds(applicant):
    return (
        ApplicantRefund.objects.filter(
            applicant=applicant,
        )
        .select_related(
            "created_by",
            "approved_by",
        )
        .prefetch_related(
            "receipts",
        )
        .order_by(
            "-refund_date",
            "-created_at",
        )
    )


def get_refund_receipts(applicant):
    return (
        ApplicantRefundReceipt.objects.filter(
            applicant=applicant,
        )
        .select_related(
            "refund",
            "generated_by",
        )
        .order_by(
            "-generated_at",
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
    from .models import Applicant, FakeLiveResult

    classification = get_status_classification()
    approved_ids = classification["approved_ids"]
    rejected_ids = classification["rejected_ids"]

    app_stats = Applicant.objects.filter(
        is_deleted=False,
    ).aggregate(
        total=Count("id"),
        approved=Count("id", filter=Q(status_id__in=approved_ids)),
        rejected=Count("id", filter=Q(status_id__in=rejected_ids)),
    )

    fake_stats = FakeLiveResult.objects.aggregate(
        total=Count("id"),
        approved=Count("id", filter=Q(status_id__in=approved_ids)),
        rejected=Count("id", filter=Q(status_id__in=rejected_ids)),
    )

    app_total = app_stats["total"] or 0
    app_approved = app_stats["approved"] or 0
    app_rejected = app_stats["rejected"] or 0
    app_processing = max(0, app_total - app_approved - app_rejected)

    fake_total = fake_stats["total"] or 0
    fake_approved = fake_stats["approved"] or 0
    fake_rejected = fake_stats["rejected"] or 0
    fake_processing = max(0, fake_total - fake_approved - fake_rejected)

    total = app_total + fake_total
    approved = app_approved + fake_approved
    rejected = app_rejected + fake_rejected
    processing = app_processing + fake_processing

    return {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "processing": processing,
        "real_total": app_total,
        "fake_total": fake_total,
        "base_served": 17000,
        "real_approved": app_approved,
        "fake_approved": fake_approved,
        "real_rejected": app_rejected,
        "fake_rejected": fake_rejected,
        "real_processing": app_processing,
        "fake_processing": fake_processing,
    }


def get_staff_statistics(staff):
    classification = get_status_classification()
    approved_ids = classification["approved_ids"]
    rejected_ids = classification["rejected_ids"]

    stats = Applicant.objects.filter(
        slot__staff=staff,
        is_deleted=False,
    ).aggregate(
        total=Count("id"),
        real_approved=Count("id", filter=Q(status_id__in=approved_ids)),
        real_rejected=Count("id", filter=Q(status_id__in=rejected_ids)),
    )

    real_total = stats["total"] or 0
    real_approved = stats["real_approved"] or 0
    real_rejected = stats["real_rejected"] or 0
    real_processing = max(0, real_total - real_approved - real_rejected)

    fake_approved = getattr(staff, "fake_approved_count", 0) or 0
    fake_rejected = getattr(staff, "fake_rejected_count", 0) or 0
    fake_processing = getattr(staff, "fake_processing_count", 0) or 0

    approved = real_approved + fake_approved
    rejected = real_rejected + fake_rejected
    processing = real_processing + fake_processing
    total = real_total + fake_approved + fake_rejected + fake_processing

    return {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "processing": processing,
        "real_approved": real_approved,
        "real_rejected": real_rejected,
        "real_processing": real_processing,
        "fake_approved": fake_approved,
        "fake_rejected": fake_rejected,
        "fake_processing": fake_processing,
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
