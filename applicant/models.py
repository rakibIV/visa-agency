from cloudinary.models import CloudinaryField
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal

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
    validate_profile_image_dimensions,
    validate_nid_number,
    validate_passport_number,
    validate_phone_number,
)
from core.choices import (
    Gender,
    MaritalStatus,
    AddressType,
    PaymentMethod,
    PaymentInstallmentType,
    ReceiptType,
    AgreementLanguage,
    ClauseVisibilityMode,
    DocumentType,
    RefundStatus,
    RefundType,
    RefundBasis,
    RefundMethodPreference,
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

    code = models.SlugField(
        max_length=160,
        unique=True,
        blank=True,
        help_text="Stable API/admin code for this agreement template.",
    )

    sequence = models.PositiveIntegerField(
        default=1,
        db_index=True,
        help_text="Order in which this agreement appears.",
    )

    title_en = models.CharField(
        max_length=200,
        blank=True,
    )

    title_ar = models.CharField(
        max_length=200,
        blank=True,
    )

    title_bn = models.CharField(
        max_length=200,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    body = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Legacy fallback body. Prefer structured clauses. Supports "
            "dynamic placeholders such as "
            "{full_name}, {passport_number}, {visa}, {job}, "
            "{country}, {payment}, {staff}, and similar values."
        ),
    )

    version = models.PositiveIntegerField(
        default=1,
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_default = models.BooleanField(
        default=False,
        help_text="Can be generated automatically for new applicants.",
    )

    class Meta:
        ordering = [
            "sequence",
            "-version",
            "title",
        ]

        verbose_name = "Agreement Template"
        verbose_name_plural = "Agreement Templates"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "sequence",
                    "version",
                ],
                name="unique_sequence_version",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(
                f"seq-{self.sequence}-{self.title}-v{self.version}"
            )

        if not self.title_en:
            self.title_en = self.title

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (v{self.version})"


class AgreementTemplateClause(BaseModel):
    template = models.ForeignKey(
        AgreementTemplate,
        on_delete=models.CASCADE,
        related_name="clauses",
    )

    clause_key = models.SlugField(
        max_length=160,
        blank=True,
        help_text="Stable key such as refund-authorization.",
    )

    clause_number = models.PositiveIntegerField(
        default=1,
    )

    title_en = models.CharField(
        max_length=255,
        blank=True,
    )

    title_ar = models.CharField(
        max_length=255,
        blank=True,
    )

    title_bn = models.CharField(
        max_length=255,
        blank=True,
    )

    body_en = models.TextField(
        blank=True,
    )

    body_ar = models.TextField(
        blank=True,
    )

    body_bn = models.TextField(
        blank=True,
    )

    visibility_mode = models.CharField(
        max_length=20,
        choices=ClauseVisibilityMode.choices,
        default=ClauseVisibilityMode.ALL,
    )

    countries = models.ManyToManyField(
        "country.Country",
        related_name="agreement_clauses",
        blank=True,
        help_text=(
            "Used with visibility_mode. INCLUDE means only these countries; "
            "EXCLUDE means hide for these countries."
        ),
    )

    visibility_rules = models.JSONField(
        default=dict,
        blank=True,
        help_text="Optional future rules for status, visa, payment, refund, etc.",
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "template",
            "clause_number",
            "created_at",
        ]

        verbose_name = "Agreement Template Clause"
        verbose_name_plural = "Agreement Template Clauses"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "template",
                    "clause_number",
                ],
                name="unique_agreement_template_clause_number",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.clause_key:
            self.clause_key = slugify(
                self.title_en or self.title_bn or self.title_ar or self.clause_number
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.template.title} | Clause {self.clause_number}"


# ==========================================================
# Core Applicant
# ==========================================================


class Applicant(SoftDeleteModel):
    application_id = models.CharField(
        max_length=8,
        unique=True,
        editable=False,
        db_index=True,
    )

    full_name = models.CharField(
        max_length=200,
        db_index=True,
    )

    photo = CloudinaryField('image', validators=[
        image_extension_validator,
        validate_image_size,
        validate_profile_image_dimensions,
    ], blank=True, null=True)

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

    secondary_job = models.ForeignKey(
        "visa.VisaJob",
        on_delete=models.PROTECT,
        related_name="secondary_applicants",
        null=True,
        blank=True,
        help_text="Optional secondary job choice.",
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

    lawyer = models.ForeignKey(
        "agency.Lawyer",
        on_delete=models.SET_NULL,
        related_name="applicants",
        null=True,
        blank=True,
        help_text="Dedicated lawyer for this applicant's email communication.",
    )

    payment_plan_installments = models.PositiveSmallIntegerField(
        default=2,
        choices=(
            (2, "Two Installments"),
            (3, "Three Installments"),
        ),
        help_text="Total expected payment installments for this applicant.",
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


class ApplicantAgreement(BaseModel):
    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name="agreements",
    )

    template = models.ForeignKey(
        AgreementTemplate,
        on_delete=models.SET_NULL,
        related_name="applicant_agreements",
        null=True,
        blank=True,
    )


    language = models.CharField(
        max_length=10,
        choices=AgreementLanguage.choices,
        default=AgreementLanguage.ALL,
        help_text="Preferred display language; rendered content stores all languages.",
    )

    title = models.CharField(
        max_length=255,
    )

    template_version = models.PositiveIntegerField(
        default=1,
    )

    rendered_content = models.JSONField(
        default=dict,
        blank=True,
        help_text="Rendered multilingual structured agreement clauses.",
    )

    rendered_text = models.JSONField(
        default=dict,
        blank=True,
        help_text="Rendered plain text by language for quick preview.",
    )

    context_snapshot = models.JSONField(
        default=dict,
        blank=True,
    )

    template_snapshot = models.JSONField(
        default=dict,
        blank=True,
    )

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="generated_applicant_agreements",
        null=True,
        blank=True,
    )

    generated_at = models.DateTimeField(
        default=timezone.now,
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_void = models.BooleanField(
        default=False,
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = [
            "-generated_at",
            "-created_at",
        ]

        verbose_name = "Applicant Agreement"
        verbose_name_plural = "Applicant Agreements"

        indexes = [
            models.Index(
                fields=[
                    "applicant",
                ],
            ),
            models.Index(
                fields=[
                    "template",
                    "is_active",
                ],
            ),
        ]

    def __str__(self):
        return f"{self.applicant.application_id} | {self.title}"


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

    preferred_refund_method = models.CharField(
        max_length=20,
        choices=RefundMethodPreference.choices,
        default=RefundMethodPreference.BANK,
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
    exchange_rate = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Exchange rate snapshot from CurrencyFreaks at the time of payment.",
    )

    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    payment_number = models.PositiveIntegerField(
        editable=False,
        help_text="Auto-generated payment sequence per applicant.",
    )

    installment_type = models.CharField(
        max_length=20,
        choices=PaymentInstallmentType.choices,
        default=PaymentInstallmentType.INITIAL,
        db_index=True,
        help_text="Identifies refund bucket and payment progress.",
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


class ApplicantMoneyReceipt(BaseModel):
    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name="money_receipts",
    )

    payment = models.ForeignKey(
        ApplicantPayment,
        on_delete=models.SET_NULL,
        related_name="money_receipts",
        null=True,
        blank=True,
    )

    receipt_number = models.CharField(
        max_length=60,
        unique=True,
        db_index=True,
    )

    receipt_type = models.CharField(
        max_length=30,
        choices=ReceiptType.choices,
        default=ReceiptType.MONEY_RECEIPT,
    )

    payment_reference = models.CharField(
        max_length=100,
        blank=True,
    )

    installment_type = models.CharField(
        max_length=20,
        choices=PaymentInstallmentType.choices,
    )

    installment_label = models.CharField(
        max_length=100,
        blank=True,
    )

    payment_number = models.PositiveIntegerField()

    payment_date = models.DateField()

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
    )

    currency = models.CharField(
        max_length=3,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
    )

    euro_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    applicant_snapshot = models.JSONField(
        default=dict,
        blank=True,
    )

    staff_snapshot = models.JSONField(
        default=dict,
        blank=True,
    )

    visa_job_country_snapshot = models.JSONField(
        default=dict,
        blank=True,
    )

    payment_snapshot = models.JSONField(
        default=dict,
        blank=True,
    )

    summary_text = models.TextField(
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="generated_money_receipts",
        null=True,
        blank=True,
    )

    generated_at = models.DateTimeField(
        default=timezone.now,
    )

    is_void = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "-generated_at",
            "-created_at",
        ]

        verbose_name = "Applicant Money Receipt"
        verbose_name_plural = "Applicant Money Receipts"

        indexes = [
            models.Index(
                fields=[
                    "applicant",
                    "receipt_number",
                ],
            ),
            models.Index(
                fields=[
                    "payment",
                    "is_active",
                ],
            ),
        ]

    def __str__(self):
        return f"{self.receipt_number} | {self.applicant.full_name}"


class ApplicantRefundBankDetail(BaseModel):
    applicant = models.OneToOneField(
        Applicant,
        on_delete=models.CASCADE,
        related_name="refund_bank_detail",
    )

    account_holder_name = models.CharField(
        max_length=200,
        blank=True,
    )

    bank_name = models.CharField(
        max_length=200,
        blank=True,
    )

    branch_name = models.CharField(
        max_length=200,
        blank=True,
    )

    district_name = models.CharField(
        max_length=150,
        blank=True,
    )

    account_number_or_iban = models.CharField(
        max_length=100,
        blank=True,
    )

    routing_number = models.CharField(
        max_length=100,
        blank=True,
    )

    mobile_number = models.CharField(
        max_length=30,
        blank=True,
    )

    country = models.CharField(
        max_length=100,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:
        verbose_name = "Applicant Refund Bank Detail"
        verbose_name_plural = "Applicant Refund Bank Details"

    def __str__(self):
        return f"Refund bank detail | {self.applicant.full_name}"


class ApplicantRefund(BaseModel):
    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name="refunds",
    )

    refund_status = models.CharField(
        max_length=30,
        choices=RefundStatus.choices,
        default=RefundStatus.PENDING,
        db_index=True,
    )

    refund_type = models.CharField(
        max_length=20,
        choices=RefundType.choices,
        default=RefundType.PARTIAL,
    )

    refund_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        blank=True,
    )

    refund_basis = models.CharField(
        max_length=20,
        choices=RefundBasis.choices,
        default=RefundBasis.PAYMENT,
    )

    refund_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("80.00"),
    )

    refundable_payment_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    refund_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    non_refundable_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    refund_reason = models.TextField(
        blank=True,
    )

    refund_date = models.DateField(
        default=timezone.localdate,
    )

    generated_from_rejection = models.BooleanField(
        default=False,
        db_index=True,
    )

    cheque_number = models.CharField(
        max_length=100,
        blank=True,
    )

    cheque_date = models.DateField(
        null=True,
        blank=True,
    )

    cheque_bank_name = models.CharField(
        max_length=200,
        blank=True,
    )

    cheque_branch_name = models.CharField(
        max_length=200,
        blank=True,
    )

    received_by_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of the person who collected the cash/cheque.",
    )

    bank_detail_snapshot = models.JSONField(
        default=dict,
        blank=True,
    )

    payment_summary_snapshot = models.JSONField(
        default=dict,
        blank=True,
    )

    applicant_snapshot = models.JSONField(
        default=dict,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_applicant_refunds",
        null=True,
        blank=True,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_applicant_refunds",
        null=True,
        blank=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            "-refund_date",
            "-created_at",
        ]

        verbose_name = "Applicant Refund"
        verbose_name_plural = "Applicant Refunds"

        indexes = [
            models.Index(
                fields=[
                    "applicant",
                    "refund_status",
                ],
            ),
            models.Index(
                fields=[
                    "applicant",
                    "generated_from_rejection",
                ],
            ),
        ]

    def __str__(self):
        return f"Refund | {self.applicant.full_name} | {self.refund_amount}"


class ApplicantRefundReceipt(BaseModel):
    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name="refund_receipts",
    )

    refund = models.ForeignKey(
        ApplicantRefund,
        on_delete=models.CASCADE,
        related_name="receipts",
    )

    receipt_number = models.CharField(
        max_length=60,
        unique=True,
        db_index=True,
    )

    receipt_type = models.CharField(
        max_length=30,
        choices=ReceiptType.choices,
        default=ReceiptType.REFUND_RECEIPT,
    )

    refund_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        blank=True,
    )

    refund_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    refundable_payment_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    refund_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    non_refundable_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    refund_reason = models.TextField(
        blank=True,
    )

    cheque_number = models.CharField(
        max_length=100,
        blank=True,
    )

    cheque_date = models.DateField(
        null=True,
        blank=True,
    )

    cheque_bank_name = models.CharField(
        max_length=200,
        blank=True,
    )

    cheque_branch_name = models.CharField(
        max_length=200,
        blank=True,
    )

    received_by_name = models.CharField(
        max_length=200,
        blank=True,
    )

    refund_bank_snapshot = models.JSONField(
        default=dict,
        blank=True,
    )

    applicant_snapshot = models.JSONField(
        default=dict,
        blank=True,
    )

    payment_summary_snapshot = models.JSONField(
        default=dict,
        blank=True,
    )

    summary_text = models.TextField(
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="generated_refund_receipts",
        null=True,
        blank=True,
    )

    generated_at = models.DateTimeField(
        default=timezone.now,
    )

    is_void = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "-generated_at",
            "-created_at",
        ]

        verbose_name = "Applicant Refund Receipt"
        verbose_name_plural = "Applicant Refund Receipts"

        indexes = [
            models.Index(
                fields=[
                    "applicant",
                    "receipt_number",
                ],
            ),
            models.Index(
                fields=[
                    "refund",
                    "is_active",
                ],
            ),
        ]

    def __str__(self):
        return f"{self.receipt_number} | {self.applicant.full_name}"

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

    file = CloudinaryField('raw', resource_type='raw', validators=[
        document_extension_validator,
        validate_document_size,
    ])

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


class FakeLiveResult(BaseModel):
    applicant_name = models.CharField(
        max_length=200,
    )
    
    application_id = models.CharField(
        max_length=8,
        db_index=True,
    )
    
    passport_number = models.CharField(
        max_length=20,
    )
    
    email = models.EmailField()
    
    photo = CloudinaryField('image', validators=[
        image_extension_validator,
        validate_image_size,
    ], blank=True, null=True)

    visa = models.ForeignKey(
        "visa.Visa",
        on_delete=models.CASCADE,
    )
    
    job = models.ForeignKey(
        "visa.VisaJob",
        on_delete=models.CASCADE,
    )
    
    country = models.ForeignKey(
        "country.Country",
        on_delete=models.CASCADE,
    )
    
    status = models.ForeignKey(
        "applicant.ApplicationStatus",
        on_delete=models.CASCADE,
    )
    
    result_date = models.DateTimeField(
        default=timezone.now,
    )

    class Meta:
        ordering = ["-result_date"]
        verbose_name = "Fake Live Result"
        verbose_name_plural = "Fake Live Results"

    def __str__(self):
        return f"{self.application_id} | {self.applicant_name} (Fake)"

