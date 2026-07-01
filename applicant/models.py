from django.conf import settings
from django.db import models

from applicant.utils import applicant_document_upload_path
from core.models import (
    BaseModel,
    SoftDeleteModel,
)
from core.validators import (
    document_extension_validator,
    image_extension_validator,
    validate_document_size,
    validate_image_size,
    validate_nid_number,
    validate_passport_number,
    validate_phone_number,
)
from core.choices import (
    Gender,
    MaritalStatus,
    AddressType,
    PaymentMethod,
    DocumentType,
)

from .utils import (
    applicant_photo_upload_path,
    applicant_document_upload_path,
)


# ==========================================================
# Lookup Tables
# ==========================================================


class ApplicationStatus(BaseModel):
    """
    Admin-manageable application workflow.

    Example:
        New
        Documents Pending
        Processing
        Embassy
        Medical
        Approved
        Rejected
        Delivered
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    color = models.CharField(
        max_length=20,
        blank=True,
        help_text="Badge color used in dashboard.",
    )

    is_default = models.BooleanField(
        default=False,
        help_text="Automatically assigned to new applicants.",
    )

    is_final = models.BooleanField(
        default=False,
        help_text="Approved / Rejected / Delivered etc.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "display_order",
            "name",
        ]

        verbose_name = "Application Status"
        verbose_name_plural = "Application Statuses"

    def __str__(self):
        return self.name


class ApplicantTag(BaseModel):
    """
    Flexible labels.

    Examples:
        VIP
        Urgent
        Embassy
        Medical
        Blocked
        Interview
    """

    name = models.CharField(
        max_length=60,
        unique=True,
    )

    color = models.CharField(
        max_length=20,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = [
            "display_order",
            "name",
        ]

        verbose_name = "Applicant Tag"
        verbose_name_plural = "Applicant Tags"

    def __str__(self):
        return self.name


class AgreementTemplate(BaseModel):
    """
    Agreement template.

    Example placeholders:

        {application_id}
        {full_name}
        {passport_number}
        {visa}
        {job}
        {country}
        {staff}
    """

    title = models.CharField(
        max_length=200,
    )

    visa = models.ForeignKey(
        "visa.Visa",
        on_delete=models.SET_NULL,
        related_name="agreement_templates",
        null=True,
        blank=True,
        help_text="Leave blank for a generic agreement.",
    )

    body = models.TextField(
        help_text=(
            "Supports placeholders like "
            "{full_name}, {passport_number}, "
            "{visa}, {job}, {country}."
        ),
    )

    version = models.PositiveIntegerField(
        default=1,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "-version",
            "title",
        ]

        verbose_name = "Agreement Template"
        verbose_name_plural = "Agreement Templates"

    def __str__(self):
        return f"{self.title} (v{self.version})"


# ==========================================================
# Core Applicant
# ==========================================================


class Applicant(SoftDeleteModel):
    application_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True,
    )

    full_name = models.CharField(
        max_length=200,
        db_index=True,
    )

    photo = models.ImageField(
    upload_to=applicant_photo_upload_path,
    validators=[
        image_extension_validator,
        validate_image_size,
    ],
    blank=True,
    null=True,
    )

    passport_number = models.CharField(
        max_length=20,
        validators=[
            validate_passport_number,
        ],
        db_index=True,
    )

    passport_issue_date = models.DateField(
        null=True,
        blank=True,
    )

    passport_expiry_date = models.DateField(
        null=True,
        blank=True,
    )

    nid_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            validate_nid_number,
        ],
    )

    date_of_birth = models.DateField()

    place_of_birth = models.CharField(
        max_length=150,
        blank=True,
    )

    visa = models.ForeignKey(
        "visa.Visa",
        on_delete=models.PROTECT,
        related_name="applicants",
    )

    job = models.ForeignKey(
        "visa.VisaJob",
        on_delete=models.PROTECT,
        related_name="applicants",
    )

    current_country = models.CharField(
        max_length=100,
        blank=True,
        help_text="Current country of residence.",
    )

    status = models.ForeignKey(
        ApplicationStatus,
        on_delete=models.PROTECT,
        related_name="applicants",
    )

    slot = models.ForeignKey(
        "staff.StaffMonthlySlot",
        on_delete=models.SET_NULL,
        related_name="applicants",
        null=True,
        blank=True,
    )

    agreement = models.ForeignKey(
        AgreementTemplate,
        on_delete=models.PROTECT,
        related_name="applicants",
        null=True,
        blank=True,
    )

    tags = models.ManyToManyField(
        ApplicantTag,
        related_name="applicants",
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
        help_text="Internal permanent remarks.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_applicants",
        null=True,
        blank=True,
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_applicants",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        verbose_name = "Applicant"
        verbose_name_plural = "Applicants"

        indexes = [
            models.Index(
                fields=[
                    "application_id",
                ],
            ),
            models.Index(
                fields=[
                    "passport_number",
                ],
            ),
            models.Index(
                fields=[
                    "status",
                ],
            ),
            models.Index(
                fields=[
                    "visa",
                ],
            ),
            models.Index(
                fields=[
                    "job",
                ],
            ),
            models.Index(
                fields=[
                    "slot",
                ],
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "passport_number",
                    "visa",
                    "job",
                ],
                name="unique_passport_visa_job",
            ),
        ]

    def __str__(self):
        return f"{self.application_id} | {self.full_name}"


class ApplicantProfile(BaseModel):
    applicant = models.OneToOneField(
        Applicant,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    father_name = models.CharField(
        max_length=150,
        blank=True,
    )

    mother_name = models.CharField(
        max_length=150,
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            validate_phone_number,
        ],
    )

    email = models.EmailField(
        blank=True,
    )

    occupation = models.CharField(
        max_length=150,
        blank=True,
    )

    highest_education = models.CharField(
        max_length=150,
        blank=True,
    )

    religion = models.CharField(
        max_length=100,
        blank=True,
    )

    marital_status = models.CharField(
        max_length=20,
        choices=MaritalStatus.choices,
        blank=True,
    )

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
    )

    nationality = models.CharField(
        max_length=100,
        blank=True,
    )

    emergency_contact_name = models.CharField(
        max_length=150,
        blank=True,
    )

    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            validate_phone_number,
        ],
    )

    emergency_contact_relation = models.CharField(
        max_length=100,
        blank=True,
    )

    class Meta:
        verbose_name = "Applicant Profile"
        verbose_name_plural = "Applicant Profiles"

    def __str__(self):
        return f"Profile | {self.applicant.full_name}"


class ApplicantAddress(BaseModel):
    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    address_type = models.CharField(
        max_length=20,
        choices=AddressType.choices,
    )

    village = models.CharField(
        max_length=150,
        blank=True,
    )

    post_office = models.CharField(
        max_length=150,
        blank=True,
    )

    police_station = models.CharField(
        max_length=150,
        blank=True,
    )

    district = models.CharField(
        max_length=150,
        blank=True,
    )

    country = models.ForeignKey(
        "country.Country",
        on_delete=models.PROTECT,
        related_name="applicant_addresses",
    )

    extra_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Flexible address data for non-Bangladesh "
            "addresses (state, province, zip code, etc.)."
        ),
    )

    class Meta:
        ordering = [
            "address_type",
        ]

        verbose_name = "Applicant Address"
        verbose_name_plural = "Applicant Addresses"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "applicant",
                    "address_type",
                ],
                name="unique_applicant_address_type",
            ),
        ]

    def __str__(self):
        return (
            f"{self.applicant.full_name} | "
            f"{self.get_address_type_display()}"
        )


class ApplicantPayment(BaseModel):
    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    payment_number = models.PositiveIntegerField(
        editable=False,
        help_text="Auto-generated payment sequence per applicant.",
    )

    receipt_number = models.CharField(
        max_length=50,
        blank=True,
    )

    payment_date = models.DateField()

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
    )

    currency = models.CharField(
        max_length=3,
        help_text="ISO Currency Code (USD, EUR, BDT, etc.).",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text="Exchange rate used during payment.",
    )

    euro_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        help_text="Calculated automatically.",
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bank transaction / Bkash / Nagad reference.",
    )

    received_by = models.ForeignKey(
        "staff.Staff",
        on_delete=models.SET_NULL,
        related_name="received_payments",
        null=True,
        blank=True,
    )

    note = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = [
            "payment_number",
        ]

        verbose_name = "Applicant Payment"
        verbose_name_plural = "Applicant Payments"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "applicant",
                    "payment_number",
                ],
                name="unique_payment_number_per_applicant",
            ),
        ]

    def __str__(self):
        return (
            f"{self.applicant.full_name} "
            f"| Payment #{self.payment_number}"
        )
    

class ApplicantStatusHistory(BaseModel):
    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name="status_history",
    )

    old_status = models.ForeignKey(
        ApplicationStatus,
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
    )

    new_status = models.ForeignKey(
        ApplicationStatus,
        on_delete=models.PROTECT,
        related_name="+",
    )

    remarks = models.TextField(
        blank=True,
    )

    changed_by = models.ForeignKey(
        "staff.Staff",
        on_delete=models.SET_NULL,
        related_name="status_changes",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        verbose_name = "Applicant Status History"
        verbose_name_plural = "Applicant Status Histories"

    def __str__(self):
        old = self.old_status.name if self.old_status else "None"

        return (
            f"{self.applicant.application_id} | "
            f"{old} → {self.new_status.name}"
        )


class ApplicantDocument(BaseModel):
    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
    )

    title = models.CharField(
        max_length=150,
        blank=True,
        help_text="Required when document type is 'Other'.",
    )

    file = models.FileField(
    upload_to=applicant_document_upload_path,
    validators=[
        document_extension_validator,
        validate_document_size,
    ],
)

    remarks = models.TextField(
        blank=True,
        help_text="Admin remarks regarding this document.",
    )

    verified = models.BooleanField(
        default=False,
    )

    verified_by = models.ForeignKey(
        "staff.Staff",
        on_delete=models.SET_NULL,
        related_name="verified_documents",
        null=True,
        blank=True,
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            "document_type",
            "created_at",
        ]

        verbose_name = "Applicant Document"
        verbose_name_plural = "Applicant Documents"

    def __str__(self):
        return (
            f"{self.applicant.full_name} | "
            f"{self.get_document_type_display()}"
        )


class ApplicantNote(BaseModel):
    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name="notes",
    )

    staff = models.ForeignKey(
        "staff.Staff",
        on_delete=models.PROTECT,
        related_name="applicant_notes",
    )

    note = models.TextField()

    is_private = models.BooleanField(
        default=True,
        help_text="Private notes are visible only to internal staff.",
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        verbose_name = "Applicant Note"
        verbose_name_plural = "Applicant Notes"

    def __str__(self):
        return (
            f"{self.applicant.application_id} | "
            f"{self.created_at:%Y-%m-%d %H:%M}"
        )

