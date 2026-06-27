import uuid


def generate_application_id():
    return f"APP-{uuid.uuid4().hex[:8].upper()}"


def applicant_photo_upload_path(instance, filename):
    extension = filename.split(".")[-1]
    return f"applicants/{instance.application_id}.{extension}"


def staff_photo_upload_path(instance, filename):
    extension = filename.split(".")[-1]
    return f"staff/{instance.id}.{extension}"


def country_flag_upload_path(instance, filename):
    extension = filename.split(".")[-1]
    return f"countries/{instance.slug}.{extension}"


def visa_category_image_upload_path(instance, filename):
    extension = filename.split(".")[-1]
    return f"visa-categories/{instance.slug}.{extension}"