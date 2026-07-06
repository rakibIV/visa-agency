# Generated manually to seed statuses

from django.db import migrations
from django.utils.text import slugify

def seed_statuses(apps, schema_editor):
    ApplicationStatus = apps.get_model("applicant", "ApplicationStatus")

    # 1. Disable (must be default)
    disable_status, created = ApplicationStatus.objects.get_or_create(
        name="Disable",
        defaults={
            "slug": slugify("Disable"),
            "description": "Initial inactive status.",
            "is_default": True,
            "display_order": 1,
            "is_active": True,
        }
    )
    if not created and not disable_status.is_default:
        # Unset all other defaults
        ApplicationStatus.objects.update(is_default=False)
        disable_status.is_default = True
        disable_status.save(update_fields=["is_default"])
    elif created:
        ApplicationStatus.objects.exclude(pk=disable_status.pk).update(is_default=False)

    # 2. First Payment Received
    ApplicationStatus.objects.get_or_create(
        name="First Payment Received",
        defaults={
            "slug": slugify("First Payment Received"),
            "description": "The first installment has been received.",
            "display_order": 2,
            "is_active": True,
        }
    )

    # 3. Profile Created
    ApplicationStatus.objects.get_or_create(
        name="Profile Created",
        defaults={
            "slug": slugify("Profile Created"),
            "description": "Profile activated after first payment.",
            "display_order": 3,
            "is_active": True,
        }
    )

def reverse_seed_statuses(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0002_alter_applicant_photo_alter_applicantdocument_file'),
    ]

    operations = [
        migrations.RunPython(seed_statuses, reverse_seed_statuses),
    ]
