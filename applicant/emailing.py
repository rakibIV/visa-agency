import os
import re
from decimal import Decimal

from django.core.mail import EmailMessage, get_connection
from django.db import transaction
from rest_framework.exceptions import ValidationError

from agency.models import Lawyer, EmailTemplate


EMAIL_PLACEHOLDER_PATTERN = re.compile(
    r"{{\s*(?P<key>[a-zA-Z0-9_]+)\s*}}"
)


def _normalize_env_key(env_key):
    if not env_key:
        raise ValidationError(
            {
                "sender": "Sender environment key is required."
            }
        )

    return str(env_key).strip().upper().replace(" ", "_")


def _resolve_sender_credentials(sender):
    smtp_email = getattr(sender, "smtp_email", None) or getattr(sender, "email", None)
    smtp_password = getattr(sender, "smtp_password", None)
    
    if smtp_email and smtp_password:
        return smtp_email, smtp_password

    env_key = _normalize_env_key(getattr(sender, "env_key", ""))

    email = os.getenv(f"{env_key}_EMAIL")
    password = os.getenv(f"{env_key}_PASSWORD")

    if not email or not password:
        raise ValidationError(
            {
                "sender": (
                    f"Missing Gmail credentials for {sender.name}. "
                    f"Expected environment variables: {env_key}_EMAIL and {env_key}_PASSWORD."
                )
            }
        )

    return email, password


def _render_text(template_text, context):
    if not template_text:
        return ""

    def replace(match):
        key = match.group("key")
        value = context.get(key, "")
        return "" if value is None else str(value)

    return EMAIL_PLACEHOLDER_PATTERN.sub(
        replace,
        template_text,
    )


def build_email_context(
    *,
    applicant,
    staff_name="",
    **extra_context
):
    from agency.models import CompanyInformation
    company = CompanyInformation.objects.first()
    company_name = company.company_name if company else "System Administrator"
    company_logo = company.company_logo.url if company and company.company_logo else ""
    company_tagline = company.tagline if company and hasattr(company, 'tagline') else ""
    company_logo_display = "inline-block" if company_logo else "none"
    
    context = {
        "applicant_name": applicant.full_name,
        "applicant_id": applicant.application_id,
        "passport_number": applicant.passport_number,
        "visa": applicant.visa.name,
        "country": applicant.visa.country.name,
        "staff": staff_name or "",
        "current_status": applicant.status.name if applicant.status else "",
        "company_name": company_name,
        "company_logo": company_logo,
        "company_tagline": company_tagline,
        "company_logo_display": company_logo_display,
    }
    context.update(extra_context)
    return context


def get_template_for_status(status):
    return (
        EmailTemplate.objects.filter(
            status=status,
            is_active=True,
        )
        .select_related(
            "status",
        )
        .first()
    )


def get_template_by_name(name):
    return (
        EmailTemplate.objects.filter(
            name__iexact=name,
            is_active=True,
        )
        .first()
    )


def render_email_template(
    *,
    template,
    context,
):
    subject = _render_text(
        template.subject,
        context,
    )

    body = _render_text(
        template.body,
        context,
    )

    return subject, body


def send_email_from_sender(
    *,
    sender,
    recipient_email,
    subject,
    body,
):
    sender_email, sender_password = _resolve_sender_credentials(sender)

    connection = get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host="smtp.gmail.com",
        port=587,
        username=sender_email,
        password=sender_password,
        use_tls=True,
        fail_silently=False,
    )

    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=sender.email,
        to=[
            recipient_email,
        ],
        connection=connection,
    )
    message.reply_to = [
        sender.email,
    ]
    message.content_subtype = "html"

    result = message.send(fail_silently=False)
    
    print(f"\n=======================================================")
    print(f"EMAIL SENT SUCCESSFULLY!")
    print(f"Recipient: {recipient_email}")
    print(f"Subject: {subject}")
    print(f"From: {sender.email}")
    print(f"=======================================================\n")
    
    return result

@transaction.atomic
def send_applicant_email(
    *,
    applicant,
    sender=None,
    template,
    staff_name="",
    **extra_context
):
    if sender is None:
        sender = getattr(applicant, "lawyer", None)

    recipient_email = getattr(
        getattr(applicant, "profile", None),
        "email",
        "",
    )

    if not recipient_email:
        raise ValidationError(
            {
                "applicant": "Applicant email address is missing."
            }
        )

    if sender is None:
        from staff.models import Staff
        admin_staff = Staff.objects.filter(user__is_superuser=True).exclude(smtp_email="").first()

        class SystemSender:
            def __init__(self, staff=None):
                if staff:
                    self.smtp_email = staff.smtp_email
                    self.smtp_password = staff.smtp_password
                    self.name = staff.user.get_full_name() or "System Administrator"
                    self.email = staff.smtp_email
                else:
                    self.env_key = os.getenv("SYSTEM_ENV_KEY", "SYSTEM")
                    self.name = os.getenv("SYSTEM_EMAIL_USERNAME", "System Administrator")
                    self.email = os.getenv(f"{self.env_key}_EMAIL")
                
        sender = SystemSender(admin_staff)

        if not sender.email:
            raise ValidationError(
                {
                    "sender": "No lawyer assigned and system fallback email is not configured."
                }
            )

    context = build_email_context(
        applicant=applicant,
        staff_name=staff_name,
        **extra_context
    )

    subject, body = render_email_template(
        template=template,
        context=context,
    )

    send_email_from_sender(
        sender=sender,
        recipient_email=recipient_email,
        subject=subject,
        body=body,
    )

    return {
        "recipient_email": recipient_email,
        "sender_email": sender.email,
        "subject": subject,
        "body": body,
    }


def get_staff_display_name(user):
    if not user or not getattr(user, "is_authenticated", False):
        return ""

    full_name = user.get_full_name()

    if full_name:
        return full_name

    return user.get_username()

