from django.db import models

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


class MaritalStatus(models.TextChoices):
    SINGLE = "SINGLE", "Single"
    MARRIED = "MARRIED", "Married"
    DIVORCED = "DIVORCED", "Divorced"
    WIDOWED = "WIDOWED", "Widowed"


class DocumentType(models.TextChoices):
    PASSPORT = "PASSPORT", "Passport"
    BIRTH_CERTIFICATE = "BIRTH_CERTIFICATE", "Birth Certificate"
    NID = "NID", "National ID"
    PHOTO = "PHOTO", "Photograph"
    IELTS = "IELTS", "IELTS Certificate"
    BANK_STATEMENT = "BANK_STATEMENT", "Bank Statement"
    MEDICAL = "MEDICAL", "Medical Report"
    POLICE_CLEARANCE = "POLICE_CLEARANCE", "Police Clearance"
    EDUCATIONAL = "EDUCATIONAL", "Educational Certificate"
    OTHER = "OTHER", "Other"