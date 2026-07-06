from cloudinary.models import CloudinaryField
from django.db import models
from django.utils.text import slugify
from core.choices import RequirementType

from core.models import BaseModel
from core.validators import (
    image_extension_validator,
    validate_image_size,
)


class Country(BaseModel):
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

    code = models.CharField(
        max_length=3,
        unique=True,
        db_index=True,
        help_text="ISO Country Code (e.g. IT, CA, AU)",
    )

    nationality = models.CharField(
        max_length=100,
        blank=True,
    )

    language = models.CharField(
    max_length=50,  # Increased to safely fit any language name
    default="English",
    help_text="The official language of the country",
    )

    flag = CloudinaryField('image', validators=[
        image_extension_validator,
        validate_image_size,
    ], blank=True, null=True)

    currency = models.CharField(
        max_length=3,
        default="USD",
        help_text="The official 3-letter currency code (e.g., USD, EUR)",
    )

    capital = models.CharField(
    max_length=100,
    blank=True,
    help_text="The capital city of the country (e.g., Washington D.C., Paris).",
    )

    time_zone = models.CharField(
    max_length=50,
    default="UTC",
    help_text="The primary time zone of the country.",
    )

    processing_time = models.CharField(
    max_length=50,
    blank=True,
    help_text="Estimated processing time phrase (e.g., '3-5 business days', '2 weeks').",
    )

    image = CloudinaryField('image', validators=[
        image_extension_validator,
        validate_image_size,
    ], blank=True, null=True, help_text="Beautiful featured image of this country.")

    short_description = models.CharField(
        max_length=255,
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
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    
class CountryRequirement(BaseModel):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="requirements",
    )

    requirement_type = models.CharField(
        max_length=20,
        choices=RequirementType.choices,
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
        ordering = ["display_order", "title"]

        verbose_name = "Country Requirement"

        verbose_name_plural = "Country Requirements"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "country",
                    "requirement_type",
                    "title",
                ],
                name="unique_country_requirement",
            )
        ]

        indexes = [
            models.Index(
                fields=[
                    "country",
                    "requirement_type",
                ]
            ),
            models.Index(
                fields=[
                    "country",
                    "is_active",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.country.name} | "
            f"{self.get_requirement_type_display()} | "
            f"{self.title}"
        )
    

class CountryFAQ(BaseModel):
    country = models.ForeignKey(
        Country,
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
        verbose_name = "Country FAQ"
        verbose_name_plural = "Country FAQs"

    def __str__(self):
        return f"{self.country.name} - {self.question}"
    

class CountryGallery(BaseModel):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="gallery",
    )

    image = CloudinaryField('image', validators=[
        image_extension_validator,
        validate_image_size,
    ])

    caption = models.CharField(
        max_length=255,
        blank=True,
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
            "id",
        ]
        verbose_name = "Country Gallery"
        verbose_name_plural = "Country Gallery"

    def __str__(self):
        return f"{self.country.name} Image"
    

class CountrySEO(BaseModel):
    country = models.OneToOneField(
        Country,
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

    meta_keywords = models.TextField(
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
        verbose_name = "Country SEO"
        verbose_name_plural = "Country SEO"

    def __str__(self):
        return f"{self.country.name} SEO"
    

