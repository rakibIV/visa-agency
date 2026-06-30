from decimal import Decimal
import re

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


# -----------------------------
# Passport Number
# -----------------------------
PASSPORT_REGEX = re.compile(r"^[A-Za-z0-9]{6,20}$")


def validate_passport_number(value):
    if not PASSPORT_REGEX.match(value):
        raise ValidationError(
            "Passport number must contain 6-20 letters or numbers."
        )


# -----------------------------
# Bangladesh NID
# -----------------------------
NID_REGEX = re.compile(r"^\d{10}$|^\d{13}$|^\d{17}$")


def validate_nid_number(value):
    if value and not NID_REGEX.match(value):
        raise ValidationError(
            "NID must be 10, 13 or 17 digits."
        )


# -----------------------------
# Phone Number
# -----------------------------
PHONE_REGEX = re.compile(r"^\+?[0-9]{8,15}$")


def validate_phone_number(value):
    if value and not PHONE_REGEX.match(value):
        raise ValidationError(
            "Enter a valid phone number."
        )


# -----------------------------
# Positive Amount
# -----------------------------
def validate_positive_amount(value):
    if value <= Decimal("0"):
        raise ValidationError(
            "Amount must be greater than zero."
        )


# -----------------------------
# Percentage
# -----------------------------
def validate_percentage(value):
    if value < 0 or value > 100:
        raise ValidationError(
            "Percentage must be between 0 and 100."
        )


# -----------------------------
# Image Size
# -----------------------------
def validate_image_size(image):
    max_size = 2 * 1024 * 1024  # 5 MB

    if image.size > max_size:
        raise ValidationError(
            "Image size cannot exceed 5 MB."
        )


# -----------------------------
# PDF Size
# -----------------------------
def validate_pdf_size(file):
    max_size = 10 * 1024 * 1024  # 10 MB

    if file.size > max_size:
        raise ValidationError(
            "PDF size cannot exceed 10 MB."
        )


# -----------------------------
# File Extension Validators
# -----------------------------
image_extension_validator = FileExtensionValidator(
    allowed_extensions=[
        "jpg",
        "png",
    ]
)

pdf_extension_validator = FileExtensionValidator(
    allowed_extensions=[
        "pdf",
    ]
)

# -----------------------------
# Applicant Document (image or PDF)
# -----------------------------
document_extension_validator = FileExtensionValidator(
    allowed_extensions=[
        "pdf",
        "jpg",
        "jpeg",
        "png",
    ]
)

def validate_document_size(file):
    max_size = 10 * 1024 * 1024  # 10 MB

    if file.size > max_size:
        raise ValidationError(
            "Document size cannot exceed 10 MB."
        )