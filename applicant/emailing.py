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

    # Determine lawyer
    lawyer = sender if isinstance(sender, Lawyer) else getattr(applicant, "lawyer", None)
    if not lawyer:
        lawyer = Lawyer.objects.filter(is_default=True, is_active=True).first()

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

    context = {
        "applicant_name": applicant.full_name,
        "applicant_id": applicant.application_id,
        "father_name": father_name,
        "nid": nid_number,
        "nid_number": nid_number,
        "passport_number": applicant.passport_number,
        "job": job_title,
        "visa": applicant.visa.name if getattr(applicant, "visa", None) else "",
        "country": applicant.visa.country.name if getattr(applicant, "visa", None) and getattr(applicant.visa, "country", None) else "",
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


def _format_body_content(body_text):
    if any(tag in body_text for tag in ["<p>", "<div>", "<table>", "<br", "<p "]):
        return body_text
    
    paragraphs = [p.strip().replace("\n", "<br>") for p in body_text.split("\n\n") if p.strip()]
    if not paragraphs:
        return body_text
    return "".join(f"<p style='margin: 0 0 16px 0; line-height: 1.6; color: #334155;'>{p}</p>" for p in paragraphs)


def wrap_in_predesigned_email_template(content, context):
    company_name = context.get("company_name", "System Administrator")
    company_logo = context.get("company_logo", "")
    company_tagline = context.get("company_tagline", "")
    company_logo_display = context.get("company_logo_display", "none")

    current_status = str(context.get("current_status", "")).lower()
    is_rejected = "reject" in current_status

    if is_rejected:
        status_box_css = """
    .status-box { background: linear-gradient(to right, #fef2f2, #ffffff); border-left: 4px solid #ef4444; border-right: 1px solid #fee2e2; border-top: 1px solid #fee2e2; border-bottom: 1px solid #fee2e2; padding: 20px 25px; margin: 25px 0; border-radius: 0 8px 8px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    .status-label { font-size: 12px; text-transform: uppercase; color: #991b1b; font-weight: 700; letter-spacing: 1px; display: block; margin-bottom: 8px; }
    .status-value { font-size: 18px; color: #b91c1c; font-weight: 800; margin: 0; display: inline-block; padding: 4px 12px; background-color: #fee2e2; border-radius: 20px; }
        """
        content = content.replace("#eff6ff", "#fef2f2").replace("#3b82f6", "#ef4444").replace("#1d4ed8", "#b91c1c").replace("#dbeafe", "#fee2e2")
    else:
        status_box_css = """
    .status-box { background: linear-gradient(to right, #eff6ff, #ffffff); border-left: 4px solid #3b82f6; border-right: 1px solid #e2e8f0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; padding: 20px 25px; margin: 25px 0; border-radius: 0 8px 8px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    .status-label { font-size: 12px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 1px; display: block; margin-bottom: 8px; }
    .status-value { font-size: 18px; color: #1d4ed8; font-weight: 800; margin: 0; display: inline-block; padding: 4px 12px; background-color: #dbeafe; border-radius: 20px; }
        """

    logo_td = f"""<td valign="middle" style="padding-right: 15px; display: {company_logo_display}"><img src="{company_logo}" alt="{company_name}" class="header-logo" onerror="this.style.display='none'" /></td>""" if company_logo else ""

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <style>
    body {{ font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #334155; margin: 0; padding: 0; }}
    .container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
    .header {{ background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 35px 30px; color: #ffffff; }}
    .header-logo {{ max-width: 55px; height: auto; border-radius: 6px; display: block; }}
    .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; text-align: left; color: #ffffff; }}
    .tagline {{ margin: 4px 0 0 0; font-size: 14px; font-weight: 400; opacity: 0.9; letter-spacing: 0.5px; text-align: left; color: #e0f2fe; }}
    .content {{ padding: 40px 35px; line-height: 1.7; font-size: 15px; color: #334155; }}
    {status_box_css}
    .footer {{ background-color: #f8fafc; padding: 25px 35px; text-align: left; font-size: 13px; color: #64748b; border-top: 1px solid #e2e8f0; }}
  </style>
</head>
<body>
  <div class='container'>
    <div class='header'>
      <table width='100%' cellpadding='0' cellspacing='0' border='0'>
        <tr>
          <td align='center'>
            <table cellpadding='0' cellspacing='0' border='0' style='margin: 0 auto;'>
              <tr>
                {logo_td}
                <td valign='middle' align='left'>
                  <h1>{company_name}</h1>
                  {f"<p class='tagline'>{company_tagline}</p>" if company_tagline else ""}
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
      <p style='margin: 0; font-size: 12px; color: #94a3b8; text-align: center;'>&copy; {company_name}. All rights reserved.</p>
    </div>
  </div>
</body>
</html>"""


def _apply_lawyer_signature(body, context):
    lawyer_name = context.get("lawyer_name")
    if not lawyer_name:
        return body

    lawyer_address = context.get("lawyer_address", "")
    address_html = f"<br><span style='color: #475569; font-size: 13px; font-weight: 400; display: block; margin-top: 2px;'>{lawyer_address}</span>" if lawyer_address else ""
    lawyer_sig_content = (
        f"Best regards<br>"
        f"<strong style='color: #0f172a; font-size: 15px; display: block; margin-top: 4px;'>{lawyer_name}</strong>"
        f"<span style='color: #64748b; font-size: 13px; font-weight: 500; display: block; margin-top: 2px;'>Legal Representative</span>"
        f"{address_html}"
    )

    # 1. Match full paragraph <p>Best regards...</p>
    match_p = re.search(r"<p[^>]*>\s*Best\s+regards.*?</p>", body, re.IGNORECASE | re.DOTALL)
    if match_p:
        replacement = f"<p style='margin-top: 24px;'>{lawyer_sig_content}</p>"
        return body[:match_p.start()] + replacement + body[match_p.end():]

    # 2. Match non-paragraph Best regards...
    match_plain = re.search(r"Best\s+regards.*", body, re.IGNORECASE | re.DOTALL)
    if match_plain:
        replacement = f"<p style='margin-top: 24px;'>{lawyer_sig_content}</p>"
        return body[:match_plain.start()] + replacement

    return body + f"<p style='margin-top: 24px;'>{lawyer_sig_content}</p>"


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

    body = _apply_lawyer_signature(body, context)

    if body.strip().startswith("<!DOCTYPE") or body.strip().startswith("<html"):
        return subject, body

    formatted_content = _format_body_content(body)
    full_html = wrap_in_predesigned_email_template(formatted_content, context)
    return subject, full_html


def send_email_from_sender(
    *,
    sender,
    recipient_email,
    subject,
    body,
):
    try:
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

