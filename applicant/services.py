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
    Applicant,
    ApplicantAddress,
    ApplicantProfile,
    CurrencyRate,
    ApplicantPayment,
    ApplicantStatusHistory,
    ApplicantDocument,
    ApplicantNote,
)
from .utils import generate_application_id

from decimal import Decimal

from django.utils import timezone
from .utils import (
    generate_payment_number,
)


@transaction.atomic
def create_applicant(
    *,
    profile_data=None,
    **applicant_data,
):
    """
    Creates an applicant together with the profile.
    """

    application_id = generate_application_id()

    applicant = Applicant.objects.create(
        application_id=application_id,
        **applicant_data,
    )

    ApplicantProfile.objects.create(
        applicant=applicant,
        **(profile_data or {}),
    )

    return applicant


@transaction.atomic
def update_applicant(
    *,
    applicant,
    profile_data=None,
    **applicant_data,
):
    """
    Updates applicant and profile.
    """

    for field, value in applicant_data.items():
        setattr(
            applicant,
            field,
            value,
        )

    applicant.save()

    if profile_data is not None:

        profile = applicant.profile

        for field, value in profile_data.items():
            setattr(
                profile,
                field,
                value,
            )

        profile.save()

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
    received_by=None,
    receipt_number="",
    reference="",
    note="",
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

    currency = currency.upper()

    exchange_rate = get_exchange_rate(
        from_currency=currency,
        to_currency=DEFAULT_TARGET_CURRENCY,
    )

    currency_rate = CurrencyRate.objects.filter(
        base_currency=currency.upper(),
        target_currency=DEFAULT_TARGET_CURRENCY,
    ).order_by(
        "-fetched_at",
    ).first()

    euro_amount = (
        Decimal(amount)
        * exchange_rate
    ).quantize(
        Decimal("0.01")
    )

    payment = ApplicantPayment.objects.create(
        applicant=applicant,
        currency_rate=currency_rate,
        payment_number=payment_number,
        payment_date=payment_date,
        payment_method=payment_method,
        currency=currency,
        amount=amount,
        exchange_rate=exchange_rate,
        euro_amount=euro_amount,
        receipt_number=receipt_number,
        reference=reference,
        received_by=received_by,
        note=note,
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

    currency_rate = CurrencyRate.objects.filter(
        base_currency=payment.currency.upper(),
        target_currency=DEFAULT_TARGET_CURRENCY,
    ).order_by(
        "-fetched_at",
    ).first()

    payment.exchange_rate = get_exchange_rate(
        from_currency=payment.currency,
        to_currency=DEFAULT_TARGET_CURRENCY,
    )

    payment.euro_amount = (
        Decimal(payment.amount)
        * payment.exchange_rate
    ).quantize(
        Decimal("0.01")
    )

    payment.currency_rate = currency_rate

    payment.save()

    return payment


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
        if sender is None:
            raise ValidationError(
                {
                    "sender": "Email sender is required when send_email is true."
                }
            )

        template = get_template_for_status(new_status)

        if template is None:
            raise ValidationError(
                {
                    "status": (
                        "No active email template is linked to this status."
                    )
                }
            )

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

    applicant.assigned_staff = slot.staff

    applicant.save(
        update_fields=[
            "slot",
            "assigned_staff",
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
    applicant.assigned_staff = None

    applicant.save(
        update_fields=[
            "slot",
            "assigned_staff",
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
