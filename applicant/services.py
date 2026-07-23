from django.db import transaction
from rest_framework.exceptions import ValidationError
from .currency import (
    DEFAULT_TARGET_CURRENCY,
    get_exchange_rate,
)
from .emailing import (
    get_staff_display_name,
    get_template_for_status,
    send_applicant_email,
)

from .models import (
    AgreementTemplate,
    AgreementTemplateClause,
    Applicant,
    ApplicantAddress,
    ApplicantAgreement,
    ApplicantProfile,
    ApplicantPayment,
    ApplicantMoneyReceipt,
    ApplicantRefund,
    ApplicantRefundBankDetail,
    ApplicantRefundReceipt,
    ApplicantStatusHistory,
    ApplicationStatus,
    ApplicantDocument,
    ApplicantNote,
)
from core.choices import (
    AgreementLanguage,
    ClauseVisibilityMode,
    PaymentInstallmentType,
    PaymentMethod,
    RefundStatus,
)
from .utils import generate_application_id

from decimal import Decimal

from django.utils import timezone
from .utils import (
    generate_payment_number,
    generate_receipt_number,
)


class SafeFormatDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


REFUND_PERCENTAGE = Decimal("80.00")
REFUND_MULTIPLIER = Decimal("0.80")


def _display_user(user):
    if not user:
        return ""

    full_name = user.get_full_name()
    return full_name or getattr(user, "username", "") or str(user)


def _staff_snapshot(staff):
    if not staff:
        return {}

    return {
        "id": str(staff.id),
        "employee_id": staff.employee_id,
        "name": _display_user(staff.user),
        "designation": getattr(staff.designation, "name", ""),
        "office": getattr(staff.office, "name", ""),
        "phone": staff.phone,
    }


def build_applicant_snapshot(applicant):
    profile = getattr(applicant, "profile", None)
    date_of_birth = getattr(applicant, "date_of_birth", None)

    if hasattr(date_of_birth, "isoformat"):
        date_of_birth_value = date_of_birth.isoformat()
    else:
        date_of_birth_value = date_of_birth

    return {
        "id": str(applicant.id),
        "application_id": applicant.application_id,
        "full_name": applicant.full_name,
        "passport_number": applicant.passport_number,
        "nid_number": applicant.nid_number,
        "date_of_birth": date_of_birth_value,
        "current_country": applicant.current_country,
        "status": getattr(applicant.status, "name", ""),
        "phone": getattr(profile, "phone", ""),
        "email": getattr(profile, "email", ""),
    }


def build_visa_job_country_snapshot(applicant):
    return {
        "visa": {
            "id": str(applicant.visa_id),
            "name": getattr(applicant.visa, "name", ""),
        },
        "job": {
            "id": str(applicant.job_id),
            "title": getattr(applicant.job, "title", ""),
        },
        "country": {
            "id": str(getattr(applicant.visa, "country_id", "")),
            "name": getattr(getattr(applicant.visa, "country", None), "name", ""),
        },
    }


def build_payment_receipt_snapshot(payment):
    return {
        "id": str(payment.id),
        "payment_number": payment.payment_number,
        "receipt_number": payment.receipt_number,
        "installment_type": payment.installment_type,
        "installment_label": payment.get_installment_type_display(),
        "payment_date": payment.payment_date.isoformat()
        if payment.payment_date
        else None,
        "payment_method": payment.payment_method,
        "payment_method_label": payment.get_payment_method_display(),
        "currency": payment.currency,
        "amount": str(payment.amount),
        "exchange_rate": str(payment.exchange_rate),
        "euro_amount": str(payment.euro_amount),
        "reference": payment.reference,
        "note": payment.note,
    }


def build_refund_bank_snapshot(bank_detail):
    if not bank_detail:
        return {
            "is_missing": True,
        }

    return {
        "is_missing": False,
        "account_holder_name": bank_detail.account_holder_name,
        "bank_name": bank_detail.bank_name,
        "branch_name": bank_detail.branch_name,
        "district_name": bank_detail.district_name,
        "account_number_or_iban": bank_detail.account_number_or_iban,
        "routing_number": bank_detail.routing_number,
        "mobile_number": bank_detail.mobile_number,
        "country": bank_detail.country,
        "notes": bank_detail.notes,
    }


def build_payment_summary_snapshot(applicant):
    payments = applicant.payments.order_by(
        "payment_number",
    )

    items = [
        {
            "id": str(payment.id),
            "payment_number": payment.payment_number,
            "installment_type": payment.installment_type,
            "installment_label": payment.get_installment_type_display(),
            "payment_date": payment.payment_date.isoformat()
            if payment.payment_date
            else None,
            "currency": payment.currency,
            "amount": str(payment.amount),
            "euro_amount": str(payment.euro_amount),
            "payment_method": payment.payment_method,
            "reference": payment.reference,
        }
        for payment in payments
    ]

    total_paid = sum(
        (payment.euro_amount for payment in payments),
        Decimal("0.00"),
    )

    refundable_total = sum(
        (
            payment.euro_amount
            for payment in payments
            if payment.installment_type
            in [
                PaymentInstallmentType.SECOND,
                PaymentInstallmentType.THIRD,
            ]
        ),
        Decimal("0.00"),
    )

    return {
        "payment_plan_installments": applicant.payment_plan_installments,
        "total_paid_euro": str(total_paid),
        "refundable_payment_total_euro": str(refundable_total),
        "payments": items,
    }


def build_refund_receipt_snapshot(refund):
    return {
        "id": str(refund.id),
        "refund_status": refund.refund_status,
        "refund_percentage": str(refund.refund_percentage),
        "refundable_payment_total": str(refund.refundable_payment_total),
        "refund_amount": str(refund.refund_amount),
        "non_refundable_amount": str(refund.non_refundable_amount),
        "refund_reason": refund.refund_reason,
        "refund_date": refund.refund_date.isoformat()
        if refund.refund_date
        else None,
        "generated_from_rejection": refund.generated_from_rejection,
    }


def build_money_receipt_summary(payment):
    return (
        f"Received {payment.amount} {payment.currency} "
        f"({payment.euro_amount} EUR) from {payment.applicant.full_name} "
        f"for {payment.get_installment_type_display()}."
    )


def build_refund_receipt_summary(refund):
    return (
        f"Refund amount {refund.refund_amount} EUR for "
        f"{refund.applicant.full_name}; {refund.refund_percentage}% of "
        f"{refund.refundable_payment_total} EUR refundable payments."
    )


def _get_company_snapshot():
    from agency.models import CompanyInformation

    company = CompanyInformation.objects.filter(
        is_active=True,
    ).first()

    if not company:
        return {}

    return {
        "id": str(company.id),
        "company_name": company.company_name,
        "phone": company.phone,
        "address": company.address,
    }


def build_agreement_context(applicant):
    payment_summary = build_payment_summary_snapshot(
        applicant,
    )
    refund_breakdown = calculate_refund_breakdown(
        applicant,
    )
    company = _get_company_snapshot()
    assigned_staff = getattr(
        getattr(applicant, "slot", None),
        "staff",
        None,
    )
    latest_refund = applicant.refunds.order_by(
        "-created_at",
    ).first()

    context = {
        "full_name": applicant.full_name,
        "application_id": applicant.application_id,
        "passport_number": applicant.passport_number,
        "visa": getattr(applicant.visa, "name", ""),
        "job": getattr(applicant.job, "title", ""),
        "country": getattr(getattr(applicant.visa, "country", None), "name", ""),
        "staff": _staff_snapshot(assigned_staff).get("name", ""),
        "company_name": company.get("company_name", ""),
        "company_phone": company.get("phone", ""),
        "company_address": company.get("address", ""),
        "refund_percentage": str(refund_breakdown["refund_percentage"]),
        "refundable_payment_total": str(
            refund_breakdown["refundable_payment_total"]
        ),
        "refund_amount": str(refund_breakdown["refund_amount"]),
        "non_refundable_amount": str(
            refund_breakdown["non_refundable_amount"]
        ),
        "first_installment": str(
            next(
                (
                    payment.euro_amount
                    for payment in applicant.payments.order_by("payment_number")
                    if payment.installment_type == PaymentInstallmentType.INITIAL
                ),
                Decimal("0.00"),
            )
        ),
        "payment_plan_installments": applicant.payment_plan_installments,
        "total_paid_euro": payment_summary["total_paid_euro"],
        "representative_name": _staff_snapshot(assigned_staff).get("name", ""),
        "refund_reason": getattr(latest_refund, "refund_reason", ""),
    }

    return {
        "flat": context,
        "applicant": build_applicant_snapshot(
            applicant,
        ),
        "visa_job_country": build_visa_job_country_snapshot(
            applicant,
        ),
        "payment_summary": payment_summary,
        "refund_breakdown": {
            key: str(value)
            for key, value in refund_breakdown.items()
        },
        "company": company,
        "staff": _staff_snapshot(
            assigned_staff,
        ),
    }


def render_agreement_text(text, context):
    return (text or "").format_map(
        SafeFormatDict(
            context.get(
                "flat",
                {},
            )
        )
    )


def is_clause_visible_for_applicant(clause, applicant):
    if not clause.is_active:
        return False

    country_id = getattr(
        applicant.visa,
        "country_id",
        None,
    )

    if clause.visibility_mode == ClauseVisibilityMode.ALL:
        return True

    country_ids = set(
        clause.countries.values_list(
            "id",
            flat=True,
        )
    )

    if clause.visibility_mode == ClauseVisibilityMode.INCLUDE:
        return country_id in country_ids

    if clause.visibility_mode == ClauseVisibilityMode.EXCLUDE:
        return country_id not in country_ids

    return True


def _template_title_by_language(template, language):
    if language == AgreementLanguage.ARABIC:
        return template.title_ar or template.title_en or template.title

    if language == AgreementLanguage.BANGLA:
        return template.title_bn or template.title_en or template.title

    return template.title_en or template.title


def _clause_title_by_language(clause, language):
    if language == AgreementLanguage.ARABIC:
        return clause.title_ar or clause.title_en or clause.title_bn

    if language == AgreementLanguage.BANGLA:
        return clause.title_bn or clause.title_en or clause.title_ar

    return clause.title_en or clause.title_bn or clause.title_ar


def _clause_body_by_language(clause, language):
    if language == AgreementLanguage.ARABIC:
        return clause.body_ar or clause.body_en or clause.body_bn

    if language == AgreementLanguage.BANGLA:
        return clause.body_bn or clause.body_en or clause.body_ar

    return clause.body_en or clause.body_bn or clause.body_ar


def render_agreement_template_for_applicant(template, applicant):
    context = build_agreement_context(
        applicant,
    )
    clauses = [
        clause
        for clause in template.clauses.prefetch_related(
            "countries",
        ).order_by(
            "clause_number",
        )
        if is_clause_visible_for_applicant(
            clause,
            applicant,
        )
    ]

    if not clauses and template.body:
        clauses = [
            AgreementTemplateClause(
                template=template,
                clause_number=1,
                title_en=template.title_en or template.title,
                title_ar=template.title_ar,
                title_bn=template.title_bn,
                body_en=template.body,
            )
        ]

    content = {}
    text = {}

    for language in [
        AgreementLanguage.ENGLISH,
        AgreementLanguage.ARABIC,
        AgreementLanguage.BANGLA,
    ]:
        rendered_clauses = []

        for clause in clauses:
            rendered_clauses.append(
                {
                    "clause_number": clause.clause_number,
                    "clause_key": clause.clause_key,
                    "title": render_agreement_text(
                        _clause_title_by_language(
                            clause,
                            language,
                        ),
                        context,
                    ),
                    "body": render_agreement_text(
                        _clause_body_by_language(
                            clause,
                            language,
                        ),
                        context,
                    ),
                }
            )

        content[language] = {
            "title": render_agreement_text(
                _template_title_by_language(
                    template,
                    language,
                ),
                context,
            ),
            "clauses": rendered_clauses,
        }
        text[language] = "\n\n".join(
            [
                f"{item['clause_number']}. {item['title']}\n{item['body']}"
                for item in rendered_clauses
            ]
        )

    return {
        "template": {
            "id": str(template.id),
            "title": template.title,
            "code": template.code,
            "sequence": template.sequence,
            "version": template.version,
        },
        "context": context,
        "rendered_content": content,
        "rendered_text": text,
    }


@transaction.atomic
def generate_applicant_agreement(
    *,
    applicant,
    template,
    language=AgreementLanguage.ALL,
    generated_by=None,
    notes="",
    force_new=False,
):
    if not template.is_active:
        raise ValidationError(
            {
                "template": "Agreement template is inactive."
            }
        )

    if not force_new:
        existing = ApplicantAgreement.objects.filter(
            applicant=applicant,
            template=template,
            is_active=True,
            is_void=False,
        ).first()

        if existing:
            return existing

    rendered = render_agreement_template_for_applicant(
        template,
        applicant,
    )

    agreement = ApplicantAgreement.objects.create(
        applicant=applicant,
        template=template,
        language=language,
        title=rendered["rendered_content"][AgreementLanguage.ENGLISH]["title"],
        template_version=template.version,
        rendered_content=rendered["rendered_content"],
        rendered_text=rendered["rendered_text"],
        context_snapshot=rendered["context"],
        template_snapshot=rendered["template"],
        generated_by=generated_by,
        notes=notes,
    )

    return agreement


@transaction.atomic
def regenerate_applicant_agreement(
    *,
    applicant_agreement,
    generated_by=None,
    notes="",
):
    if applicant_agreement.template is None:
        raise ValidationError(
            {
                "template": "Original agreement template is no longer available."
            }
        )

    applicant_agreement.is_active = False
    applicant_agreement.is_void = True
    applicant_agreement.save(
        update_fields=[
            "is_active",
            "is_void",
            "updated_at",
        ],
    )

    return generate_applicant_agreement(
        applicant=applicant_agreement.applicant,
        template=applicant_agreement.template,
        language=applicant_agreement.language,
        generated_by=generated_by,
        notes=notes or applicant_agreement.notes,
        force_new=True,
    )


def preview_applicant_agreement(
    *,
    applicant,
    template,
):
    return render_agreement_template_for_applicant(
        template,
        applicant,
    )


@transaction.atomic
def generate_default_applicant_agreements(
    *,
    applicant,
    generated_by=None,
):
    agreements = []

    for template in AgreementTemplate.objects.filter(
        is_active=True,
    ).order_by(
        "sequence",
        "-version",
    ):
        agreements.append(
            generate_applicant_agreement(
                applicant=applicant,
                template=template,
                generated_by=generated_by,
            )
        )

    return agreements


def _get_status_by_name_or_slug(name):
    from django.db.models import Q

    slug = name.lower().replace(" ", "-")
    
    # Aliases for system-critical statuses to handle user variations (e.g. typos, numbers)
    aliases = {
        "1st Payment recieved": ["first payment received", "first payment", "1st payment", "1st payment received", "1st payment recieved"],
        "Profile Created": ["profile created"],
        "Payment Confirmed": ["payment confirmed"],
    }
    
    query = Q(slug=slug) | Q(name__iexact=name)
    
    if name in aliases:
        for alias in aliases[name]:
            alias_slug = alias.lower().replace(" ", "-")
            query = query | Q(slug=alias_slug) | Q(name__iexact=alias)
            
    return ApplicationStatus.objects.filter(query, is_active=True).first()


def _is_rejected_status(status):
    name_lower = getattr(status, "name", "").lower()
    slug_lower = getattr(status, "slug", "").lower()
    return (
        "reject" in name_lower
        or "reject" in slug_lower
    )


def get_applicant_payment_summary(applicant):
    return build_payment_summary_snapshot(applicant)


def get_refundable_payment_total(applicant):
    return sum(
        (
            payment.euro_amount
            for payment in applicant.payments.filter(
                installment_type__in=[
                    PaymentInstallmentType.SECOND,
                    PaymentInstallmentType.THIRD,
                ],
            )
        ),
        Decimal("0.00"),
    ).quantize(
        Decimal("0.01")
    )


def calculate_refund_breakdown(applicant):
    refundable_total = get_refundable_payment_total(
        applicant,
    )
    refund_amount = (
        refundable_total
        * REFUND_MULTIPLIER
    ).quantize(
        Decimal("0.01")
    )
    non_refundable_amount = (
        refundable_total
        - refund_amount
    ).quantize(
        Decimal("0.01")
    )

    return {
        "refund_percentage": REFUND_PERCENTAGE,
        "refundable_payment_total": refundable_total,
        "refund_amount": refund_amount,
        "non_refundable_amount": non_refundable_amount,
    }


def is_payment_confirmed(applicant):
    required_installment = (
        PaymentInstallmentType.THIRD
        if applicant.payment_plan_installments == 3
        else PaymentInstallmentType.SECOND
    )

    return applicant.payments.filter(
        installment_type=required_installment,
    ).exists()


def _sync_payment_status(applicant, changed_by=None):
    if is_payment_confirmed(applicant):
        status = _get_status_by_name_or_slug("Payment Confirmed")
        if status and applicant.status != status:
            change_applicant_status(
                applicant=applicant,
                new_status=status,
                changed_by=changed_by,
                remarks="Status updated automatically from payment progress.",
            )
            
        # Generate default agreements when payment is confirmed
        from applicant.services import generate_default_applicant_agreements
        generate_default_applicant_agreements(applicant=applicant)
            
        return

    if applicant.payments.filter(installment_type=PaymentInstallmentType.INITIAL).exists():
        first_payment_status = _get_status_by_name_or_slug("1st Payment recieved")
        profile_created_status = _get_status_by_name_or_slug("Profile Created")
        
        # Transition to First Payment Received
        if first_payment_status and applicant.status != first_payment_status and applicant.status != profile_created_status:
            change_applicant_status(
                applicant=applicant,
                new_status=first_payment_status,
                changed_by=changed_by,
                remarks="First payment received.",
                send_email=bool(applicant.lawyer),
                sender=applicant.lawyer,
            )
            
        # Immediately transition to Profile Created
        if profile_created_status and applicant.status != profile_created_status:
            change_applicant_status(
                applicant=applicant,
                new_status=profile_created_status,
                changed_by=changed_by,
                remarks="Profile automatically activated after first payment.",
                send_email=bool(applicant.lawyer),
                sender=applicant.lawyer,
            )


@transaction.atomic
def create_applicant(
    *,
    profile_data=None,
    refund_bank_detail_data=None,
    **applicant_data,
):
    """
    Creates an applicant together with the profile and refund bank details.
    """

    application_id = applicant_data.pop("application_id", None)
    if application_id:
        application_id = str(application_id).strip()
        if not application_id:
            application_id = None
    else:
        application_id = None

    applicant = Applicant.objects.create(
        application_id=application_id,
        **applicant_data,
    )

    ApplicantProfile.objects.create(
        applicant=applicant,
        **(profile_data or {}),
    )

    if refund_bank_detail_data is not None:
        ApplicantRefundBankDetail.objects.create(
            applicant=applicant,
            **refund_bank_detail_data,
        )

    return applicant


@transaction.atomic
def update_applicant(
    *,
    applicant,
    profile_data=None,
    refund_bank_detail_data=None,
    **applicant_data,
):
    """
    Updates applicant, profile, and refund bank details.
    """

    for field, value in applicant_data.items():
        setattr(
            applicant,
            field,
            value,
        )

    applicant.save()

    if profile_data is not None:

        profile = getattr(applicant, "profile", None)
        if profile is None:
            profile = ApplicantProfile.objects.create(applicant=applicant)

        for field, value in profile_data.items():
            setattr(
                profile,
                field,
                value,
            )

        profile.save()

    if refund_bank_detail_data is not None:
        bank_detail = getattr(applicant, "refund_bank_detail", None)
        if bank_detail is None:
            ApplicantRefundBankDetail.objects.create(
                applicant=applicant,
                **refund_bank_detail_data,
            )
        else:
            for field, value in refund_bank_detail_data.items():
                setattr(
                    bank_detail,
                    field,
                    value,
                )
            bank_detail.save()

    return applicant


@transaction.atomic
def create_applicant_address(
    *,
    applicant,
    **address_data,
):
    """
    Creates an applicant address.
    """

    return ApplicantAddress.objects.create(
        applicant=applicant,
        **address_data,
    )


@transaction.atomic
def update_applicant_address(
    *,
    applicant_address,
    **address_data,
):
    """
    Updates an applicant address.
    """

    for field, value in address_data.items():
        setattr(
            applicant_address,
            field,
            value,
        )

    applicant_address.save()

    return applicant_address


@transaction.atomic
def create_payment(
    *,
    applicant,
    payment_date,
    payment_method,
    currency,
    amount,
    installment_type=PaymentInstallmentType.INITIAL,
    received_by=None,
    receipt_number="",
    reference="",
    note="",
    generated_by=None,
):
    """
    Creates a payment for an applicant.

    - Auto payment number
    - Fetches live exchange rate from Currency Freaks
    - Calculates euro amount
    """

    payment_number = generate_payment_number(
        applicant,
    )

    try:
        exchange_rate = get_exchange_rate(from_currency=currency.upper())
    except Exception as e:
        exchange_rate = Decimal("1.0000")

    euro_amount = (
        Decimal(amount)
        * exchange_rate
    ).quantize(
        Decimal("0.01")
    )

    payment = ApplicantPayment.objects.create(
        applicant=applicant,
        exchange_rate=exchange_rate,
        payment_number=payment_number,
        installment_type=installment_type,
        payment_date=payment_date,
        payment_method=payment_method,
        currency=currency.upper(),
        amount=amount,
        euro_amount=euro_amount,
        receipt_number=receipt_number,
        reference=reference,
        received_by=received_by,
        note=note,
    )

    generate_money_receipt_for_payment(
        payment,
        generated_by=generated_by,
    )

    _sync_payment_status(
        applicant,
        changed_by=received_by,
    )

    return payment

@transaction.atomic
def update_payment(
    *,
    payment,
    **payment_data,
):
    """
    Updates an existing payment.
    Re-fetches exchange rate if currency changes.
    """

    for field, value in payment_data.items():
        setattr(
            payment,
            field,
            value,
        )

    payment.currency = payment.currency.upper()

    try:
        exchange_rate = get_exchange_rate(from_currency=payment.currency.upper())
    except Exception:
        exchange_rate = Decimal("1.0000")

    payment.exchange_rate = exchange_rate

    payment.euro_amount = (
        Decimal(payment.amount)
        * payment.exchange_rate
    ).quantize(
        Decimal("0.01")
    )

    payment.save()

    _sync_payment_status(
        payment.applicant,
        changed_by=payment.received_by,
    )

    return payment


@transaction.atomic
def generate_money_receipt_for_payment(
    payment,
    generated_by=None,
    force_new=False,
):
    if not force_new:
        existing = payment.money_receipts.filter(
            is_active=True,
            is_void=False,
        ).first()

        if existing:
            return existing

    applicant = payment.applicant
    receipt_number = payment.receipt_number or generate_receipt_number(
        "MR",
    )

    if ApplicantMoneyReceipt.objects.filter(
        receipt_number=receipt_number,
    ).exists():
        receipt_number = generate_receipt_number(
            "MR",
        )

    receipt = ApplicantMoneyReceipt.objects.create(
        applicant=applicant,
        payment=payment,
        receipt_number=receipt_number,
        payment_reference=payment.reference,
        installment_type=payment.installment_type,
        installment_label=payment.get_installment_type_display(),
        payment_number=payment.payment_number,
        payment_date=payment.payment_date,
        payment_method=payment.payment_method,
        currency=payment.currency,
        amount=payment.amount,
        exchange_rate=payment.exchange_rate,
        euro_amount=payment.euro_amount,
        applicant_snapshot=build_applicant_snapshot(
            applicant,
        ),
        staff_snapshot=_staff_snapshot(
            payment.received_by,
        ),
        visa_job_country_snapshot=build_visa_job_country_snapshot(
            applicant,
        ),
        payment_snapshot=build_payment_receipt_snapshot(
            payment,
        ),
        summary_text=build_money_receipt_summary(
            payment,
        ),
        notes=payment.note,
        generated_by=generated_by,
    )

    if not payment.receipt_number:
        payment.receipt_number = receipt.receipt_number
        payment.save(
            update_fields=[
                "receipt_number",
                "updated_at",
            ],
        )

    return receipt


@transaction.atomic
def create_or_update_applicant_refund_bank_detail(
    *,
    applicant,
    **bank_data,
):
    bank_detail, _ = ApplicantRefundBankDetail.objects.update_or_create(
        applicant=applicant,
        defaults=bank_data,
    )

    return bank_detail


@transaction.atomic
def create_refund_for_rejected_applicant(
    applicant,
    created_by=None,
    reason="",
):
    if not _is_rejected_status(applicant.status):
        raise ValidationError(
            {
                "status": "Applicant must be rejected before refund generation."
            }
        )

    existing = ApplicantRefund.objects.filter(
        applicant=applicant,
        generated_from_rejection=True,
    ).exclude(
        refund_status=RefundStatus.CANCELLED,
    ).first()

    if existing:
        return existing

    breakdown = calculate_refund_breakdown(
        applicant,
    )

    if breakdown["refundable_payment_total"] <= Decimal("0.00"):
        return None

    bank_detail = getattr(
        applicant,
        "refund_bank_detail",
        None,
    )
    bank_snapshot = build_refund_bank_snapshot(
        bank_detail,
    )

    refund_status = (
        RefundStatus.BANK_INFO_MISSING
        if bank_snapshot.get("is_missing")
        else RefundStatus.PENDING
    )

    method_map = {
        "BANK": PaymentMethod.BANK,
        "MOBILE": PaymentMethod.MOBILE_BANKING,
        "CASH": PaymentMethod.CASH,
    }
    refund_method = method_map.get(bank_snapshot.get("notes"), "")

    refund = ApplicantRefund.objects.create(
        applicant=applicant,
        refund_status=refund_status,
        refund_percentage=breakdown["refund_percentage"],
        refundable_payment_total=breakdown["refundable_payment_total"],
        refund_amount=breakdown["refund_amount"],
        non_refundable_amount=breakdown["non_refundable_amount"],
        refund_method=refund_method,
        refund_reason=reason,
        generated_from_rejection=True,
        bank_detail_snapshot=bank_snapshot,
        payment_summary_snapshot=build_payment_summary_snapshot(
            applicant,
        ),
        applicant_snapshot=build_applicant_snapshot(
            applicant,
        ),
        created_by=created_by,
    )

    generate_refund_receipt_for_applicant(
        applicant,
        refund,
        generated_by=created_by,
    )

    return refund


@transaction.atomic
def generate_refund_receipt_for_applicant(
    applicant,
    refund,
    generated_by=None,
    force_new=False,
):
    if refund.applicant_id != applicant.id:
        raise ValidationError(
            {
                "refund": "Refund does not belong to this applicant."
            }
        )

    if not force_new:
        existing = refund.receipts.filter(
            is_active=True,
            is_void=False,
        ).first()

        if existing:
            return existing

    receipt = ApplicantRefundReceipt.objects.create(
        applicant=applicant,
        refund=refund,
        receipt_number=generate_receipt_number(
            "RR",
        ),
        refund_percentage=refund.refund_percentage,
        refundable_payment_total=refund.refundable_payment_total,
        refund_amount=refund.refund_amount,
        non_refundable_amount=refund.non_refundable_amount,
        refund_reason=refund.refund_reason,
        refund_method=refund.refund_method,
        cheque_number=refund.cheque_number,
        cheque_date=refund.cheque_date,
        cheque_bank_name=refund.cheque_bank_name,
        cheque_branch_name=refund.cheque_branch_name,
        received_by_name=refund.received_by_name,
        refund_bank_snapshot=refund.bank_detail_snapshot,
        applicant_snapshot=refund.applicant_snapshot,
        payment_summary_snapshot=refund.payment_summary_snapshot,
        summary_text=build_refund_receipt_summary(
            refund,
        ),
        notes=refund.notes,
        generated_by=generated_by,
    )

    return receipt


@transaction.atomic
def mark_refund_paid(
    *,
    refund,
    approved_by=None,
    notes="",
):
    refund.refund_status = RefundStatus.PAID
    refund.approved_by = approved_by
    refund.paid_at = timezone.now()

    if notes:
        refund.notes = notes

    refund.save(
        update_fields=[
            "refund_status",
            "approved_by",
            "paid_at",
            "notes",
            "updated_at",
        ],
    )

    return refund


@transaction.atomic
def change_applicant_status(
    *,
    applicant,
    new_status,
    changed_by=None,
    remarks="",
    updated_by=None,
    sender=None,
    send_email=False,
):
    """
    Changes applicant status and
    stores status history.
    """

    old_status = applicant.status

    if old_status == new_status:
        return applicant

    applicant.status = new_status

    update_fields = [
        "status",
        "updated_at",
    ]

    if updated_by is not None:
        applicant.updated_by = updated_by
        update_fields.insert(
            1,
            "updated_by",
        )

    applicant.save(
        update_fields=update_fields,
    )

    ApplicantStatusHistory.objects.create(
        applicant=applicant,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        remarks=remarks,
    )

    if send_email:

        template = get_template_for_status(new_status)

        if template is None:
            class FallbackTemplate:
                subject = "Application Status Update: {{ current_status }}"
                body = (
                    "<!DOCTYPE html>"
                    "<html>"
                    "<head>"
                    "<meta charset='utf-8'>"
                    "<style>"
                    "  body { font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #334155; margin: 0; padding: 0; }"
                    "  .container { max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }"
                    "  .header { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 35px 30px; color: #ffffff; }"
                    "  .header-logo { max-width: 55px; height: auto; border-radius: 6px; display: block; }"
                    "  .header h1 { margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; text-align: left; }"
                    "  .tagline { margin: 4px 0 0 0; font-size: 14px; font-weight: 400; opacity: 0.9; letter-spacing: 0.5px; text-align: left; }"
                    "  .content { padding: 45px 40px; line-height: 1.7; font-size: 16px; }"
                    "  .status-box { background: linear-gradient(to right, #eff6ff, #ffffff); border-left: 4px solid #3b82f6; border-right: 1px solid #e2e8f0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; padding: 20px 25px; margin: 30px 0; border-radius: 0 8px 8px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }"
                    "  .status-label { font-size: 12px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 1px; display: block; margin-bottom: 8px; }"
                    "  .status-value { font-size: 20px; color: #0f172a; font-weight: 800; margin: 0; display: inline-block; padding: 4px 12px; background-color: #dbeafe; color: #1d4ed8; border-radius: 20px; }"
                    "  .footer { background-color: #f1f5f9; padding: 25px; text-align: center; font-size: 13px; color: #64748b; border-top: 1px solid #e2e8f0; }"
                    "  .footer p { margin: 5px 0; }"
                    "</style>"
                    "</head>"
                    "<body>"
                    "  <div class='container'>"
                    "    <div class='header'>"
                    "      <table width='100%' cellpadding='0' cellspacing='0' border='0'>"
                    "        <tr>"
                    "          <td align='center'>"
                    "            <table cellpadding='0' cellspacing='0' border='0' style='margin: 0 auto;'>"
                    "              <tr>"
                    "                <td valign='middle' style='padding-right: 15px; display: {{ company_logo_display }}'>"
                    "                  <img src='{{ company_logo }}' alt='{{ company_name }}' class='header-logo' onerror='this.style.display=\"none\"' />"
                    "                </td>"
                    "                <td valign='middle' align='left'>"
                    "                  <h1>{{ company_name }}</h1>"
                    "                  <p class='tagline'>{{ company_tagline }}</p>"
                    "                </td>"
                    "              </tr>"
                    "            </table>"
                    "          </td>"
                    "        </tr>"
                    "      </table>"
                    "    </div>"
                    "    <div class='content'>"
                    "      <p>Dear <strong style='color: #0f172a;'>{{ applicant_name }}</strong>,</p>"
                    "      <p>We are writing to inform you that there has been an update regarding your application (ID: <strong style='color: #0f172a;'>{{ applicant_id }}</strong>).</p>"
                    "      <div class='status-box'>"
                    "        <span class='status-label'>New Application Status</span>"
                    "        <p class='status-value'>{{ current_status }}</p>"
                    "      </div>"
                    "      <p>If you have any questions or require further assistance, please do not hesitate to contact our team.</p>"
                    "      <p>Best regards,<br><strong style='color: #0f172a;'>The {{ company_name }} Team</strong></p>"
                    "    </div>"
                    "    <div class='footer'>"
                    "      <p>&copy; 2024 {{ company_name }}. All rights reserved.</p>"
                    "    </div>"
                    "  </div>"
                    "</body>"
                    "</html>"
                )
            template = FallbackTemplate()

        send_applicant_email(
            applicant=applicant,
            sender=sender,
            template=template,
            staff_name=get_staff_display_name(
                changed_by.user if changed_by else None
            ),
        )



    return applicant


@transaction.atomic
def send_manual_applicant_email(
    *,
    applicant,
    sender,
    template,
    sent_by=None,
):
    return send_applicant_email(
        applicant=applicant,
        sender=sender,
        template=template,
        staff_name=get_staff_display_name(
            sent_by
        ),
    )


@transaction.atomic
def assign_slot(
    *,
    applicant,
    slot,
):
    """
    Assign applicant to a monthly slot.

    Prevents assigning applicants
    beyond the allocated slot count.
    """

    allocated = slot.total_slot

    used = slot.applicants.exclude(
        pk=applicant.pk,
    ).count()

    if used >= allocated:
        raise ValidationError(
        {
            "slot": "This staff has no remaining slot."
        }
        )

    applicant.slot = slot

    applicant.save(
        update_fields=[
            "slot",
            "updated_at",
        ],
    )

    return applicant


@transaction.atomic
def remove_slot(
    *,
    applicant,
):
    """
    Removes slot assignment.
    """

    applicant.slot = None

    applicant.save(
        update_fields=[
            "slot",
            "updated_at",
        ],
    )

    return applicant


@transaction.atomic
def upload_document(
    *,
    applicant,
    document_type,
    file,
    title="",
    remarks="",
):
    """
    Upload a document for an applicant.
    """

    document = ApplicantDocument.objects.create(
        applicant=applicant,
        document_type=document_type,
        title=title,
        file=file,
        remarks=remarks,
    )

    return document


@transaction.atomic
def update_document(
    *,
    document,
    **document_data,
):
    """
    Update applicant document.
    """

    for field, value in document_data.items():
        setattr(
            document,
            field,
            value,
        )

    document.save()

    return document


@transaction.atomic
def verify_document(
    *,
    document,
    verified_by,
):
    """
    Marks a document as verified.
    """

    document.verified = True

    document.verified_by = verified_by

    document.verified_at = timezone.now()

    document.save(
        update_fields=[
            "verified",
            "verified_by",
            "verified_at",
            "updated_at",
        ],
    )

    return document


@transaction.atomic
def unverify_document(
    *,
    document,
):
    """
    Removes verification from a document.
    """

    document.verified = False

    document.verified_by = None

    document.verified_at = None

    document.save(
        update_fields=[
            "verified",
            "verified_by",
            "verified_at",
            "updated_at",
        ],
    )

    return document


@transaction.atomic
def add_note(
    *,
    applicant,
    staff,
    note,
    is_private=True,
):
    """
    Add an internal note.
    """

    return ApplicantNote.objects.create(
        applicant=applicant,
        staff=staff,
        note=note,
        is_private=is_private,
    )


@transaction.atomic
def update_note(
    *,
    applicant_note,
    note,
    is_private,
):
    """
    Update an applicant note.
    """

    applicant_note.note = note

    applicant_note.is_private = is_private

    applicant_note.save(
        update_fields=[
            "note",
            "is_private",
            "updated_at",
        ],
    )

    return applicant_note


@transaction.atomic
def delete_note(
    *,
    applicant_note,
):
    """
    Deletes a note.
    """

    applicant_note.delete()
