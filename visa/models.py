from cloudinary.models import CloudinaryField
from django.db import models
from django.utils.text import slugify
from agency.models import AgencyService
from core.choices import VisaRequirementType
from core.validators import image_extension_validator, validate_image_size

from core.models import BaseModel
from country.models import Country


class VisaCategory(BaseModel):
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
            "name",
        ]

        verbose_name = "Visa Category"
        verbose_name_plural = "Visa Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Visa(BaseModel):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="visas",
    )

    category = models.ForeignKey(
        VisaCategory,
        on_delete=models.PROTECT,
        related_name="visas",
    )

    name = models.CharField(
        max_length=200,
        db_index=True,
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    services = models.ManyToManyField(
    AgencyService,
    related_name="visas",
    blank=True,
    )

    minimum_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    maximum_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    working_hours_per_week = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    overtime_available = models.BooleanField(
        default=False,
    )

    minimum_processing_days = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    maximum_processing_days = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    duration_in_months = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Visa validity or contract duration in months.",
    )

    from_any_country = models.BooleanField(
        default=True,
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
            "name",
        ]

        verbose_name = "Visa"
        verbose_name_plural = "Visas"

        indexes = [
            models.Index(
                fields=[
                    "country",
                    "category",
                ]
            ),
            models.Index(
                fields=[
                    "country",
                    "is_active",
                ]
            ),
            models.Index(
                fields=[
                    "category",
                    "is_active",
                ]
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                f"{self.country.name}-{self.name}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.country.name} - {self.name}"
    

class VisaJob(BaseModel):
    visa = models.ForeignKey(
        Visa,
        on_delete=models.CASCADE,
        related_name="jobs",
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    minimum_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    maximum_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    currency = models.CharField(
        max_length=10,
        default="EUR",
    )

    vacancies = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    experience_required = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: Fresher, 1 Year, 2 Years",
    )

    duty_days_per_week = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Example: 6",
    )

    duty_hours_per_day = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Example: 8.0",
    )

    overtime_available = models.BooleanField(
        default=False,
    )

    overtime_rate = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: €8/hour",
    )

    accommodation = models.BooleanField(
        default=False,
    )

    food = models.BooleanField(
        default=False,
    )

    medical = models.BooleanField(
        default=False,
    )

    transportation = models.BooleanField(
        default=False,
    )

    insurance = models.BooleanField(
        default=False,
    )

    air_ticket = models.BooleanField(
        default=False,
        help_text="Provided by employer.",
    )

    contract_duration_months = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    probation_period_months = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    location = models.CharField(
        max_length=150,
        blank=True,
        help_text="Example: Milan, Rome",
    )

    language_requirement = models.CharField(
        max_length=150,
        blank=True,
    )

    education_requirement = models.CharField(
        max_length=150,
        blank=True,
    )

    gender_preference = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional",
    )

    age_requirement = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: 21-35 Years",
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

        verbose_name = "Visa Job"

        verbose_name_plural = "Visa Jobs"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "visa",
                    "title",
                ],
                name="unique_visa_job",
            )
        ]

        indexes = [
            models.Index(
                fields=[
                    "visa",
                    "is_active",
                ]
            ),
        ]

    def __str__(self):
        return f"{self.visa.name} - {self.title}"
    


class JobFacility(BaseModel):
    job = models.ForeignKey(
        VisaJob,
        on_delete=models.CASCADE,
        related_name="facilities",
    )

    title = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )


class VisaRequirement(BaseModel):
    visa = models.ForeignKey(
        Visa,
        on_delete=models.CASCADE,
        related_name="requirements",
    )

    requirement_type = models.CharField(
        max_length=20,
        choices=VisaRequirementType.choices,
        db_index=True,
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    is_required = models.BooleanField(
        default=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "display_order",
            "title",
        ]

        verbose_name = "Visa Requirement"

        verbose_name_plural = "Visa Requirements"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "visa",
                    "requirement_type",
                    "title",
                ],
                name="unique_visa_requirement",
            )
        ]

        indexes = [
            models.Index(
                fields=[
                    "visa",
                    "requirement_type",
                ]
            ),
            models.Index(
                fields=[
                    "visa",
                    "is_active",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.visa.name} | "
            f"{self.get_requirement_type_display()} | "
            f"{self.title}"
        )


class VisaStep(BaseModel):
    visa = models.ForeignKey(
        Visa,
        on_delete=models.CASCADE,
        related_name="steps",
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField()

    display_order = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "display_order",
            "id",
        ]

        verbose_name = "Visa Step"

        verbose_name_plural = "Visa Steps"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "visa",
                    "title",
                ],
                name="unique_visa_step",
            )
        ]

        indexes = [
            models.Index(
                fields=[
                    "visa",
                    "display_order",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.visa.name} - "
            f"Step {self.display_order}"
        )


class VisaFAQ(BaseModel):
    visa = models.ForeignKey(
        Visa,
        on_delete=models.CASCADE,
        related_name="faqs",
    )

    question = models.CharField(
        max_length=255,
    )

    answer = models.TextField()

    display_order = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "display_order",
            "id",
        ]

        verbose_name = "Visa FAQ"

        verbose_name_plural = "Visa FAQs"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "visa",
                    "question",
                ],
                name="unique_visa_question",
            )
        ]

        indexes = [
            models.Index(
                fields=[
                    "visa",
                    "display_order",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.visa.name} - "
            f"{self.question}"
        )
    



class VisaSEO(BaseModel):
    visa = models.OneToOneField(
        Visa,
        on_delete=models.CASCADE,
        related_name="seo",
    )

    meta_title = models.CharField(
        max_length=255,
        blank=True,
    )

    meta_description = models.TextField(
        blank=True,
    )

    keywords = models.TextField(
        blank=True,
        help_text="Separate keywords with commas.",
    )

    canonical_url = models.URLField(
        blank=True,
    )

    og_title = models.CharField(
        max_length=255,
        blank=True,
    )

    og_description = models.TextField(
        blank=True,
    )

    og_image = CloudinaryField('image', validators=[
        image_extension_validator,
        validate_image_size,
    ], blank=True, null=True)

    class Meta:
        verbose_name = "Visa SEO"
        verbose_name_plural = "Visa SEO"

    def __str__(self):
        return f"{self.visa.name} SEO"