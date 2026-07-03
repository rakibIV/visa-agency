from django.db import models

class PaymentMethod(models.TextChoices):
    CASH = "CASH", "Hand Cash"
    BANK = "BANK", "Bank Transfer"
    MOBILE_BANKING = "MOBILE_BANKING", "Mobile Banking"
    CHEQUE = "CHEQUE", "Cheque"
    ONLINE = "ONLINE", "Online Payment"

class PaymentInstallmentType(models.TextChoices):
    INITIAL = "INITIAL", "Initial Payment"
    SECOND = "SECOND", "Second Installment"
    THIRD = "THIRD", "Third Installment"

class ReceiptType(models.TextChoices):
    MONEY_RECEIPT = "MONEY_RECEIPT", "Money Receipt"
    REFUND_RECEIPT = "REFUND_RECEIPT", "Refund Receipt"

class AgreementType(models.TextChoices):
    MAIN = "MAIN", "Main Agreement"
    SECOND = "SECOND", "Second Agreement"
    THIRD = "THIRD", "Third Agreement"
    REFUND = "REFUND", "Refund Agreement"
    OTHER = "OTHER", "Other Agreement"

class AgreementLanguage(models.TextChoices):
    ENGLISH = "en", "English"
    ARABIC = "ar", "Arabic"
    BANGLA = "bn", "Bangla"
    ALL = "all", "All Languages"

class ClauseVisibilityMode(models.TextChoices):
    ALL = "ALL", "All Countries"
    INCLUDE = "INCLUDE", "Only Selected Countries"
    EXCLUDE = "EXCLUDE", "Except Selected Countries"

class RefundStatus(models.TextChoices):
    BANK_INFO_MISSING = "bank_info_missing", "Bank Info Missing"
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"

class RefundReason(models.TextChoices):
    REJECTION = "rejection", "Application Rejection"
    CANCELLATION = "cancellation", "Applicant Cancellation"
    AGREEMENT_REFUND = "agreement_refund", "Agreement Based Refund"
    MANUAL = "manual", "Manual Refund"


class RefundType(models.TextChoices):
    PARTIAL = "partial", "Partial Refund"
    FULL = "full", "Full Refund"


class RefundBasis(models.TextChoices):
    PAYMENT = "payment", "Payment Based"
    AGREEMENT = "agreement", "Agreement Based"
    OTHER = "other", "Other"



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
