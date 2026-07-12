from cloudinary.models import CloudinaryField
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils.text import slugify

from agency.models import Office
from core.choices import Gender
from core.models import BaseModel
from core.validators import (
    image_extension_validator,
    validate_image_size,
    validate_profile_image_dimensions,
    validate_signature_dimensions,
)


class Designation(BaseModel):
    name = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
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

        verbose_name = "Designation"
        verbose_name_plural = "Designations"

    def __str__(self):
        return self.name


class Staff(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True,
    )

    designation = models.ForeignKey(
        Designation,
        on_delete=models.PROTECT,
        related_name="staffs",
    )

    office = models.ForeignKey(
        Office,
        on_delete=models.PROTECT,
        related_name="staffs",
    )

    photo = CloudinaryField('image', validators=[
        image_extension_validator,
        validate_image_size,
        validate_profile_image_dimensions,
    ], blank=True, null=True)

    signature = CloudinaryField('image', validators=[
        image_extension_validator,
        validate_image_size,
        validate_signature_dimensions,
    ], blank=True, null=True)

    phone = models.CharField(
        max_length=30,
    )

    whatsapp = models.CharField(
        max_length=30,
        blank=True,
    )

    father_name = models.CharField(
        max_length=200,
    )

    mother_name = models.CharField(
        max_length=200,
    )

    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
    )

    date_of_birth = models.DateField()

    nationality = models.CharField(
        max_length=100,
    )

    nid_number = models.CharField(
        max_length=50,
        blank=True,
    )

    passport_number = models.CharField(
        max_length=50,
        blank=True,
    )

    joining_date = models.DateField()

    reference_staff = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="referred_staffs",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "employee_id",
        ]

        verbose_name = "Staff"
        verbose_name_plural = "Staff"

    def __str__(self):
        return (
            f"{self.employee_id} - "
            f"{self.user.get_full_name()}"
        )


class StaffMonthlySlot(BaseModel):
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name="monthly_slots",
    )

    allocation_month = models.DateField(
        help_text="Always save the first day of the month.",
    )

    total_slot = models.PositiveIntegerField()

    class Meta:
        ordering = [
            "-allocation_month",
        ]

        verbose_name = "Staff Monthly Slot"
        verbose_name_plural = "Staff Monthly Slots"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "staff",
                    "allocation_month",
                ],
                name="unique_staff_month_slot",
            )
        ]

    def __str__(self):
        return (
            f"{self.staff.employee_id} | "
            f"{self.allocation_month.strftime('%B %Y')}"
        )


class SubStaff(BaseModel):
    parent_staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name="sub_staffs",
    )

    name = models.CharField(
        max_length=200,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "name",
        ]

        verbose_name = "Sub Staff"
        verbose_name_plural = "Sub Staff"

    def __str__(self):
        return f"{self.name} ({self.parent_staff.employee_id})"


class SubStaffMonthlySlot(BaseModel):
    sub_staff = models.ForeignKey(
        SubStaff,
        on_delete=models.CASCADE,
        related_name="monthly_slots",
    )

    allocation_month = models.DateField(
        help_text="Always save the first day of the month.",
    )

    allocated_slot = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = [
            "-allocation_month",
            "sub_staff__name",
        ]

        verbose_name = "Sub Staff Monthly Slot"
        verbose_name_plural = "Sub Staff Monthly Slots"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "sub_staff",
                    "allocation_month",
                ],
                name="unique_sub_staff_month_slot",
            )
        ]

    def clean(self):
        super().clean()

        if not self.sub_staff_id or not self.allocation_month:
            return

        parent_staff = self.sub_staff.parent_staff
        parent_slot = parent_staff.monthly_slots.filter(
            allocation_month=self.allocation_month,
        ).first()

        if not parent_slot:
            raise ValidationError(
                {
                    "allocation_month": (
                        "The parent staff does not have a monthly slot record "
                        "for this month."
                    )
                }
            )

        if self.allocated_slot < 0:
            raise ValidationError(
                {
                    "allocated_slot": (
                        "Allocated slots cannot be negative."
                    )
                }
            )

        allocations = SubStaffMonthlySlot.objects.filter(
            sub_staff__parent_staff=parent_staff,
            allocation_month=self.allocation_month,
        )

        if self.pk:
            allocations = allocations.exclude(pk=self.pk)

        distributed_slots = allocations.aggregate(
            total=Sum("allocated_slot"),
        )["total"] or 0

        if distributed_slots + self.allocated_slot > parent_slot.total_slot:
            raise ValidationError(
                {
                    "allocated_slot": (
                        "The total allocated slots across all sub-staff "
                        "cannot exceed the parent staff's monthly slot limit."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.sub_staff.name} | "
            f"{self.allocation_month.strftime('%B %Y')}"
        )


def default_public_staff_fields():
    return [
        "employee_id",
        "full_name",
        "photo",
        "designation",
        "office",
        "phone",
        "whatsapp",
    ]


class StaffPublicProfile(BaseModel):
    staff = models.OneToOneField(
        Staff,
        on_delete=models.CASCADE,
        related_name="public_profile",
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        blank=True,
        db_index=True,
    )

    public_password_hash = models.CharField(
        max_length=128,
        blank=True,
    )

    public_fields = models.JSONField(
        default=default_public_staff_fields,
        blank=True,
        help_text="List of staff profile fields that can be returned publicly.",
    )

    is_public = models.BooleanField(
        default=False,
        db_index=True,
    )

    class Meta:
        ordering = [
            "staff__employee_id",
        ]

        verbose_name = "Staff Public Profile"
        verbose_name_plural = "Staff Public Profiles"

    def set_public_password(self, raw_password):
        self.public_password_hash = make_password(raw_password)

    def check_public_password(self, raw_password):
        if not self.public_password_hash:
            return False

        return check_password(
            raw_password,
            self.public_password_hash,
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(
                self.staff.user.get_full_name()
                or self.staff.employee_id
            )
            base_slug = base_slug or self.staff.employee_id.lower()
            slug = base_slug
            counter = 2

            while self.__class__.objects.filter(
                slug=slug,
            ).exclude(
                pk=self.pk,
            ).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Public profile | {self.staff.employee_id}"


class StaffDocument(BaseModel):
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    title = models.CharField(
        max_length=200,
    )

    file = CloudinaryField('raw')

    display_order = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "display_order",
            "title",
        ]

        verbose_name = "Staff Document"
        verbose_name_plural = "Staff Documents"

    def __str__(self):
        return (
            f"{self.staff.employee_id} - "
            f"{self.title}"
        )


class StaffEmergencyContact(BaseModel):
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name="emergency_contacts",
    )

    name = models.CharField(
        max_length=200,
    )

    relationship = models.CharField(
        max_length=100,
    )

    phone = models.CharField(
        max_length=30,
    )

    address = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = [
            "name",
        ]

        verbose_name = "Emergency Contact"
        verbose_name_plural = "Emergency Contacts"

    def __str__(self):
        return (
            f"{self.staff.employee_id} - "
            f"{self.name}"
        )
