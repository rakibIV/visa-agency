import secrets
import string


APPLICATION_ID_PREFIX = "ARG"
APPLICATION_ID_RANDOM_LENGTH = 5
APPLICATION_ID_LENGTH = len(APPLICATION_ID_PREFIX) + APPLICATION_ID_RANDOM_LENGTH
APPLICATION_ID_ALPHABET = string.ascii_uppercase + string.digits


def generate_application_id():
    """
    Generates a unique public business application ID.

    Example:
        ARGA72Q9
    """

    from .models import Applicant

    for _ in range(100):
        suffix = "".join(
            secrets.choice(APPLICATION_ID_ALPHABET)
            for _ in range(APPLICATION_ID_RANDOM_LENGTH)
        )
        application_id = f"{APPLICATION_ID_PREFIX}{suffix}"

        if not Applicant.objects.filter(
            application_id=application_id,
        ).exists():
            return application_id

    raise RuntimeError("Unable to generate a unique application ID.")


def generate_payment_number(applicant):
    """
    Generates the next payment number
    for a specific applicant.

    Example:
        Applicant A:
            1
            2
            3

        Applicant B:
            1
            2
    """

    last_payment = (
        applicant.payments.order_by("-payment_number")
        .only("payment_number")
        .first()
    )

    if not last_payment:
        return 1

    return last_payment.payment_number + 1


def generate_receipt_number(prefix):
    """
    Generates compact receipt numbers.

    Example:
        MR-20260704-000001
        RR-20260704-000001
    """

    from django.utils import timezone
    from .models import ApplicantMoneyReceipt, ApplicantRefundReceipt

    today = timezone.localdate()
    date_part = today.strftime("%Y%m%d")

    if prefix == "RR":
        model = ApplicantRefundReceipt
    else:
        model = ApplicantMoneyReceipt

    count = model.objects.filter(
        receipt_number__startswith=f"{prefix}-{date_part}",
    ).count()

    return f"{prefix}-{date_part}-{count + 1:06d}"


def applicant_photo_upload_path(
    instance,
    filename,
):
    """
    Upload path:

    applicants/photos/APP-000001/photo.jpg
    """

    application_id = (
        instance.application_id
        or "new"
    )

    return (
        f"applicants/photos/"
        f"{application_id}/{filename}"
    )


def applicant_document_upload_path(
    instance,
    filename,
):
    """
    Upload path:

    applicants/documents/
        APP-000001/passport.pdf
    """

    application_id = (
        instance.applicant.application_id
    )

    return (
        f"applicants/documents/"
        f"{application_id}/{filename}"
    )


def build_agreement_context(
    applicant,
):
    """
    Returns placeholders used
    in agreement templates.
    """

    return {
        "application_id": applicant.application_id,
        "full_name": applicant.full_name,
        "passport_number": applicant.passport_number,
        "visa": applicant.visa.name,
        "job": applicant.job.title,
        "country": applicant.visa.country.name,
        "status": applicant.status.name,
    }

