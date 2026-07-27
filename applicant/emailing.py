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
    sender=None,
    staff_name="",
    **extra_context
):
    from agency.models import CompanyInformation, Lawyer
    company = CompanyInformation.objects.first()
    company_name = company.company_name if company else "System Administrator"
    company_logo = company.company_logo.url if company and company.company_logo else ""
    company_tagline = company.tagline if company and hasattr(company, 'tagline') else ""
    company_logo_display = "inline-block" if company_logo else "none"

    # Determine lawyer (only set if explicitly assigned)
    lawyer = sender if isinstance(sender, Lawyer) else getattr(applicant, "lawyer", None)

    lawyer_name = getattr(lawyer, "name", "") if lawyer else ""
    lawyer_address = getattr(lawyer, "address", "") if lawyer else ""
    lawyer_phone = ""
    lawyer_email = ""
    
    father_name = getattr(getattr(applicant, "profile", None), "father_name", "") or ""
    nid_number = getattr(applicant, "nid_number", "") or ""
    job_title = ""
    if getattr(applicant, "job", None) and hasattr(applicant.job, "title"):
        job_title = applicant.job.title
    elif getattr(applicant, "profile", None) and hasattr(applicant.profile, "occupation"):
        job_title = applicant.profile.occupation or ""

    company_whatsapp = getattr(company, "whatsapp", "") if company else ""
    company_signature = company.company_signature.url if company and getattr(company, "company_signature", None) else ""

    country_name = ""
    country_flag = ""
    if getattr(applicant, "visa", None) and getattr(applicant.visa, "country", None):
        c_obj = applicant.visa.country
        country_name = c_obj.name or ""
        if getattr(c_obj, "flag", None):
            try:
                country_flag = c_obj.flag.url
            except Exception:
                country_flag = ""

    context = {
        "applicant_name": applicant.full_name,
        "applicant_id": applicant.application_id,
        "father_name": father_name,
        "nid": nid_number,
        "nid_number": nid_number,
        "passport_number": applicant.passport_number,
        "job": job_title,
        "visa": applicant.visa.name if getattr(applicant, "visa", None) else "",
        "country": country_name,
        "country_name": country_name,
        "country_flag": country_flag,
        "staff": staff_name or "",
        "current_status": applicant.status.name if applicant.status else "",
        "company_name": company_name,
        "company_logo": company_logo,
        "company_tagline": company_tagline,
        "company_logo_display": company_logo_display,
        "company_whatsapp": company_whatsapp,
        "whatsapp": company_whatsapp,
        "company_signature": company_signature,
        "lawyer_name": lawyer_name,
        "lawyer_address": lawyer_address,
        "lawyer_phone": "",
        "lawyer_email": "",
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


def _format_body_content(body_text, context=None):
    if not body_text:
        return ""
    
    if context is None:
        context = {}

    current_status = str(context.get("current_status", "")).strip()
    is_rejected = "reject" in current_status.lower()

    lines = [p.strip() for p in body_text.split("\n\n") if p.strip()]
    formatted_chunks = []

    for chunk in lines:
        # If chunk is a status line like "Status: Shortlisted by Employer"
        match = re.match(r'^(?:Status|New Application Status)\s*:\s*(.*)$', chunk, re.IGNORECASE)
        if match:
            custom_status_val = match.group(1).strip() or current_status
            val_rejected = is_rejected or ("reject" in custom_status_val.lower())
            
            if val_rejected:
                box_html = (
                    f"<div class='status-box' style='background: linear-gradient(to right, #fef2f2, #ffffff); border-left: 4px solid #ef4444; border-right: 1px solid #fee2e2; border-top: 1px solid #fee2e2; border-bottom: 1px solid #fee2e2; padding: 18px 22px; margin: 24px 0; border-radius: 0 10px 10px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.02);'>"
                    f"  <span style='font-size: 11px; text-transform: uppercase; color: #991b1b; font-weight: 700; letter-spacing: 1px; display: block; margin-bottom: 6px;'>New Application Status</span>"
                    f"  <span style='font-size: 16px; color: #b91c1c; font-weight: 800; margin: 0; display: inline-block; padding: 4px 14px; background-color: #fee2e2; border-radius: 20px;'>{custom_status_val}</span>"
                    f"</div>"
                )
            else:
                box_html = (
                    f"<div class='status-box' style='background: linear-gradient(to right, #eff6ff, #ffffff); border-left: 4px solid #3b82f6; border-right: 1px solid #e2e8f0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; padding: 18px 22px; margin: 24px 0; border-radius: 0 10px 10px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.02);'>"
                    f"  <span style='font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 1px; display: block; margin-bottom: 6px;'>New Application Status</span>"
                    f"  <span style='font-size: 16px; color: #1d4ed8; font-weight: 800; margin: 0; display: inline-block; padding: 4px 14px; background-color: #dbeafe; border-radius: 20px;'>{custom_status_val}</span>"
                    f"</div>"
                )
            formatted_chunks.append(box_html)
        else:
            # Format normal paragraph
            clean_chunk = chunk.replace("\n", "<br>")
            formatted_chunks.append(f"<p style='margin: 0 0 16px 0; line-height: 1.7; color: #334155; font-size: 15px;'>{clean_chunk}</p>")

    return "".join(formatted_chunks)


def wrap_in_predesigned_email_template(content, context):
    company_name = context.get("company_name", "System Administrator")
    company_logo = context.get("company_logo", "")
    country_name = context.get("country_name") or context.get("country") or "Visa Application"
    country_flag = context.get("country_flag", "")

    # Flag TD rendering (Centered)
    flag_td = f"""<td valign="middle" style="padding-right: 12px;"><img src="{country_flag}" alt="{country_name}" style="width: 46px; height: 32px; object-fit: cover; border-radius: 6px; border: 2px solid rgba(255,255,255,0.4); display: block; box-shadow: 0 4px 10px rgba(0,0,0,0.2);" /></td>""" if country_flag else ""

    # Logo TD rendering beside reference
    logo_td = f"""<td valign="middle" style="padding-right: 8px;"><img src="{company_logo}" alt="{company_name}" style="height: 20px; width: auto; border-radius: 4px; display: inline-block; vertical-align: middle;" /></td>""" if company_logo else ""

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <style>
    body {{ font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #334155; margin: 0; padding: 0; }}
    .container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 14px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
    .header {{ background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); padding: 32px 25px; color: #ffffff; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 26px; font-weight: 900; letter-spacing: 0.5px; color: #ffffff; text-transform: uppercase; line-height: 1.1; }}
    .reference-text {{ margin: 0; font-size: 13px; font-weight: 600; color: #e0f2fe; opacity: 0.95; letter-spacing: 0.3px; }}
    .content {{ padding: 35px 30px; line-height: 1.7; font-size: 15px; color: #334155; }}
    .footer {{ background-color: #f8fafc; padding: 22px 30px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
  </style>
</head>
<body>
  <div class='container'>
    <div class='header'>
      <table width='100%' cellpadding='0' cellspacing='0' border='0'>
        <tr>
          <td align='center' valign='middle'>
            <table cellpadding='0' cellspacing='0' border='0' style='margin: 0 auto 10px auto;'>
              <tr>
                {flag_td}
                <td valign='middle' align='left'>
                  <h1>{country_name}</h1>
                </td>
              </tr>
            </table>
            <table cellpadding='0' cellspacing='0' border='0' style='margin: 0 auto;'>
              <tr>
                {logo_td}
                <td valign='middle' align='center'>
                  <p class='reference-text'>Reference: {company_name}</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </div>
    <div class='content'>
      {content}
    </div>
    <div class='footer'>
      <p style='margin: 0;'>&copy; {company_name}. All rights reserved.</p>
    </div>
  </div>
</body>
</html>"""


def _apply_lawyer_signature(body, context):
    lawyer_name = context.get("lawyer_name")
    company_name = context.get("company_name", "System Administrator")

    sig_name = lawyer_name if lawyer_name else f"The {company_name} Team"
    lawyer_address = context.get("lawyer_address", "")
    address_html = f"<div style='color: #64748b; font-size: 13px; font-weight: 400; margin-top: 3px;'>{lawyer_address}</div>" if (lawyer_name and lawyer_address) else ""
    title_html = "<div style='color: #64748b; font-size: 13px; font-weight: 600; margin-top: 2px;'>Legal Representative</div>" if lawyer_name else ""

    signature_block = (
        f"<div style='margin-top: 30px; padding-top: 20px; border-top: 1px solid #f1f5f9; text-align: left;'>"
        f"  <div style='color: #64748b; font-size: 14px; font-weight: 500; margin-bottom: 6px;'>Best regards,</div>"
        f"  <div style='color: #0f172a; font-size: 16px; font-weight: 800;'>{sig_name}</div>"
        f"  {title_html}"
        f"  {address_html}"
        f"</div>"
    )

    cleaned_body = re.sub(
        r'(?i)<p[^>]*>\s*Best\s+regards.*?</p>|Best\s+regards.*',
        '',
        body,
        flags=re.DOTALL
    ).strip()

    return cleaned_body + signature_block


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

    if body.strip().startswith("<!DOCTYPE") or body.strip().startswith("<html"):
        return subject, body

    formatted_content = _format_body_content(body, context)
    formatted_content = _apply_lawyer_signature(formatted_content, context)
    full_html = wrap_in_predesigned_email_template(formatted_content, context)
    return subject, full_html


def send_email_from_sender(
    *,
    sender,
    recipient_email,
    subject,
    body,
):
    from django.conf import settings

    sender_email = getattr(sender, "email", None) or getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@visaagency.com")

    # 1. Try custom SMTP sender connection if credentials available
    try:
        smtp_email, smtp_password = _resolve_sender_credentials(sender)
        if smtp_email and smtp_password:
            connection = get_connection(
                backend="django.core.mail.backends.smtp.EmailBackend",
                host="smtp.gmail.com",
                port=587,
                username=smtp_email,
                password=smtp_password,
                use_tls=True,
                fail_silently=False,
            )

            message = EmailMessage(
                subject=subject,
                body=body,
                from_email=sender_email,
                to=[recipient_email],
                connection=connection,
            )
            if hasattr(sender, "email") and sender.email:
                message.reply_to = [sender.email]
            message.content_subtype = "html"
            result = message.send(fail_silently=False)

            print(f"\n=======================================================")
            print(f"EMAIL SENT SUCCESSFULLY VIA SMTP!")
            print(f"Recipient: {recipient_email}")
            print(f"Subject: {subject}")
            print(f"From: {sender_email}")
            print(f"=======================================================\n")
            return result
    except Exception as exc:
        import logging
        logging.getLogger(__name__).info(f"Custom SMTP info for {sender_email}: {exc}. Retrying via default mail backend...")

    # 2. Fallback to Django default email backend
    try:
        message = EmailMessage(
            subject=subject,
            body=body,
            from_email=sender_email,
            to=[recipient_email],
        )
        message.content_subtype = "html"
        result = message.send(fail_silently=False)

        print(f"\n=======================================================")
        print(f"EMAIL SENT SUCCESSFULLY VIA DEFAULT BACKEND!")
        print(f"Recipient: {recipient_email}")
        print(f"Subject: {subject}")
        print(f"From: {sender_email}")
        print(f"=======================================================\n")
        return result
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning(f"Failed to send email to {recipient_email}: {exc}")
        return 0


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

    if not getattr(applicant, "send_email_on_status_change", True):
        import logging
        logging.getLogger(__name__).info(f"Applicant {getattr(applicant, 'id', None)} has status email toggle OFF. Skipping email notification.")
        return None

    if not recipient_email:
        import logging
        logging.getLogger(__name__).warning(f"Applicant {getattr(applicant, 'id', None)} has no email address. Skipping email notification.")
        return None

    if sender is None:
        from staff.models import Staff
        from agency.models import CompanyInformation

        admin_staff = Staff.objects.filter(user__is_superuser=True).exclude(smtp_email="").first()

        class SystemSender:
            def __init__(self, staff=None):
                if staff and getattr(staff, "smtp_email", None):
                    self.smtp_email = staff.smtp_email
                    self.smtp_password = getattr(staff, "smtp_password", "")
                    self.name = staff.user.get_full_name() or "System Administrator"
                    self.email = staff.smtp_email
                else:
                    self.env_key = os.getenv("SYSTEM_ENV_KEY", "SYSTEM")
                    self.name = os.getenv("SYSTEM_EMAIL_USERNAME", "System Administrator")
                    self.email = os.getenv(f"{self.env_key}_EMAIL")
                    self.smtp_email = self.email
                    self.smtp_password = os.getenv(f"{self.env_key}_PASSWORD")

                    if not self.email:
                        comp = CompanyInformation.objects.first()
                        if comp and getattr(comp, "email", None):
                            self.email = comp.email
                            self.smtp_email = comp.email
                            self.name = comp.company_name

        sender = SystemSender(admin_staff)

        if not getattr(sender, "email", None):
            import logging
            logging.getLogger(__name__).warning("No lawyer assigned and system fallback email is not configured. Skipping email notification.")
            return None

    context = build_email_context(
        applicant=applicant,
        sender=sender,
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
        "sender_email": getattr(sender, "email", ""),
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

