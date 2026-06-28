from django.db import models

class ApplicantStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    DOCUMENT_REQUIRED = "DOCUMENT_REQUIRED", "Document Required"
    EMBASSY = "EMBASSY", "At Embassy"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"


class PaymentMethod(models.TextChoices):
    CASH = "CASH", "Hand Cash"
    BANK = "BANK", "Bank Transfer"
    MOBILE_BANKING = "MOBILE_BANKING", "Mobile Banking"
    CHEQUE = "CHEQUE", "Cheque"
    ONLINE = "ONLINE", "Online Payment"


class InstallmentType(models.TextChoices):
    FIRST = "FIRST", "First Installment"
    SECOND = "SECOND", "Second Installment"
    THIRD = "THIRD", "Third Installment"


class Gender(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    OTHER = "OTHER", "Other"


class AddressType(models.TextChoices):
    PRESENT = "PRESENT", "Present"
    PERMANENT = "PERMANENT", "Permanent"


class StaffDesignation(models.TextChoices):
    MANAGER = "MANAGER", "Manager"
    SENIOR_EXECUTIVE = "SENIOR_EXECUTIVE", "Senior Executive"
    EXECUTIVE = "EXECUTIVE", "Executive"
    COUNSELOR = "COUNSELOR", "Counselor"
    MARKETING = "MARKETING", "Marketing"
    OTHER = "OTHER", "Other"

class SocialPlatform(models.TextChoices):
    FACEBOOK = "FACEBOOK", "Facebook"
    INSTAGRAM = "INSTAGRAM", "Instagram"
    X = "X", "X (Twitter)"
    LINKEDIN = "LINKEDIN", "LinkedIn"
    YOUTUBE = "YOUTUBE", "YouTube"
    WHATSAPP = "WHATSAPP", "WhatsApp"
    PINTEREST = "PINTEREST", "Pinterest"
    TIKTOK = "TIKTOK", "TikTok"
    OTHER = "OTHER", "Other"



class RequirementType(models.TextChoices):
    VISA = "VISA", "Visa Requirement"
    DOCUMENT = "DOCUMENT", "Document Requirement"


class VisaRequirementType(models.TextChoices):
    DOCUMENT = "DOCUMENT", "Document"
    ELIGIBILITY = "ELIGIBILITY", "Eligibility"
    BENEFIT = "BENEFIT", "Benefit"
    RESTRICTION = "RESTRICTION", "Restriction"
    NOTE = "NOTE", "Important Note"