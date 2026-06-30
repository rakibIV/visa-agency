from django.utils.text import slugify

from .models import Applicant


def generate_application_id():
    """
    Generates sequential application IDs.

    Example:
        APP-000001
        APP-000002
        APP-000003
    """

    last_applicant = (
        Applicant.objects.order_by("-id")
        .only("application_id")
        .first()
    )

    if not last_applicant:
        return "APP-000001"

    number = int(
        last_applicant.application_id.replace(
            "APP-",
            "",
        )
    )

    return f"APP-{number + 1:06d}"


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

