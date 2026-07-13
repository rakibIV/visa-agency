from cloudinary.models import CloudinaryField
from django.db import models
from django.db.models import Q
from django.utils.text import slugify

from core.models import BaseModel
from core.validators import (
    document_extension_validator,
    image_extension_validator,
    validate_document_size,
    validate_image_size,
)

from core.choices import SocialPlatform

class AgencyService(BaseModel):
    title = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
    )

    slug = models.SlugField(
        max_length=170,
        unique=True,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="React icon name or FontAwesome class.",
    )

    is_featured = models.BooleanField(
        default=False,
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
            "title",
        ]

        verbose_name = "Agency Service"
        verbose_name_plural = "Agency Services"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Notice(BaseModel):
    title = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
    )

    content = models.TextField(
        blank=True,
    )

    attachment = CloudinaryField('raw', resource_type='raw', validators=[
        document_extension_validator,
        validate_document_size,
    ], blank=True, null=True, help_text="Optional notice attachment. Allowed: PDF, JPG, JPEG, PNG. Max size: 10 MB.")

    is_pinned = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "-is_pinned",
            "-created_at",
            "title",
        ]

        verbose_name = "Notice"
        verbose_name_plural = "Notices"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Review(BaseModel):
    name = models.CharField(
        max_length=150,
    )

    comment = models.TextField()

    rating = models.PositiveSmallIntegerField(
        default=5,
        help_text="Rating from 1 to 5.",
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f"{self.name} - {self.rating}/5"


class ContactUs(BaseModel):
    name = models.CharField(
        max_length=150,
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    subject = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Lawyer(BaseModel):
    name = models.CharField(
        max_length=150,
        unique=True,
    )

    email = models.EmailField(
        unique=True,
    )

    env_key = models.CharField(
        max_length=100,
        unique=True,
        help_text="Reads credentials from <ENV_KEY>_EMAIL and <ENV_KEY>_PASSWORD.",
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    country = models.ForeignKey(
        "country.Country",
        on_delete=models.SET_NULL,
        related_name="lawyers",
        null=True,
        blank=True,
    )

    is_default = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "-is_default",
            "name",
        ]

        verbose_name = "Lawyer"
        verbose_name_plural = "Lawyers"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "is_default",
                ],
                condition=Q(is_default=True),
                name="unique_default_lawyer",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.env_key:
            self.env_key = self.env_key.strip().upper().replace(" ", "_")
        if self.email:
            self.email = self.email.strip().lower()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class EmailTemplate(BaseModel):
    name = models.CharField(
        max_length=150,
        unique=True,
    )

    status = models.OneToOneField(
        "applicant.ApplicationStatus",
        on_delete=models.SET_NULL,
        related_name="email_template",
        null=True,
        blank=True,
        help_text="Used for automatic applicant status emails.",
    )

    subject = models.CharField(
        max_length=255,
    )

    body = models.TextField(
        help_text="""
Available Variables:

{{ applicant_name }}

{{ applicant_id }}

{{ passport_number }}

{{ visa }}

{{ country }}

{{ staff }}

{{ current_status }}
""",
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "name",
        ]

        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"

    def __str__(self):
        return self.name


class CompanyInformation(BaseModel):
    company_name = models.CharField(
        max_length=255,
    )

    company_logo = CloudinaryField('image', validators=[
        image_extension_validator,
        validate_image_size,
    ], blank=True, null=True)

    favicon = CloudinaryField('image', validators=[
        image_extension_validator,
        validate_image_size,
    ], blank=True, null=True)


    phone = models.CharField(
        max_length=30,
    )

    email = models.EmailField(
        max_length=255,
        blank=True,
        null=True,
    )

    website = models.URLField(
        max_length=255,
        blank=True,
        null=True,
    )

    address = models.TextField()


    about = models.TextField(
        blank=True,
    )

    mission = models.TextField(
        blank=True,
    )

    vision = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        verbose_name = "Company Information"
        verbose_name_plural = "Company Information"

    def __str__(self):
        return self.company_name
    



class Office(BaseModel):

    company = models.ForeignKey(
    CompanyInformation,
    on_delete=models.CASCADE,
    related_name="branches",
    )
    branch_name = models.CharField(
        max_length=150,
    )

    email = models.EmailField(
        blank=True,
    )

    phone = models.CharField(
        max_length=30,
    )


    address = models.TextField()


    office_hours = models.CharField(
        max_length=150,
        blank=True,
        help_text="Example: Sat - Thu (9:00 AM - 6:00 PM)",
    )

    is_head_office = models.BooleanField(
        default=False,
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
            "branch_name",
        ]

        verbose_name = "Branch"

        verbose_name_plural = "Branches"

    def __str__(self):
        return self.branch_name
    

class SocialLink(BaseModel):
    company = models.ForeignKey(
        CompanyInformation,
        on_delete=models.CASCADE,
        related_name="social_links",
    )

    platform = models.CharField(
        max_length=50,
        choices=SocialPlatform.choices,
    )

    url = models.URLField()

    display_order = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

