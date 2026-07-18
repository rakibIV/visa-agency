import os
import sys
import django
from decimal import Decimal

# Setup Django environment
sys.path.append(r"C:\Rakib\Visa Agency Website")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Visa_Web_Service.settings")
django.setup()

import cloudinary.uploader
from country.models import Country
from visa.models import VisaCategory, Visa, VisaRequirement, VisaJob
from django.utils.text import slugify

def upload_image(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return ""
    try:
        response = cloudinary.uploader.upload(filepath)
        return response['public_id']
    except Exception as e:
        print(f"Error uploading {filepath}: {e}")
        return ""

def load_data():
    base_asset_path = r"C:\Rakib\Visa Aagency Frontend\admin\src\assets\data for load"
    
    # 1. Create or get Category
    category, created = VisaCategory.objects.get_or_create(
        name="European Work Permit",
        defaults={"slug": "european-work-permit", "description": "Professional Visa Processing & Overseas Employment Services", "is_active": True, "display_order": 1}
    )
    
    countries_data = [
        {"name": "Portugal", "code": "PT", "currency": "EUR", "language": "Portuguese"},
        {"name": "Netherlands", "code": "NL", "currency": "EUR", "language": "Dutch"},
        {"name": "Poland", "code": "PL", "currency": "PLN", "language": "Polish"},
        {"name": "Bulgaria", "code": "BG", "currency": "BGN", "language": "Bulgarian"},
        {"name": "Serbia", "code": "RS", "currency": "RSD", "language": "Serbian"},
    ]
    
    requirements = [
        "Valid Passport (Minimum 6 Months Validity)",
        "Passport Size Photograph (White Background)",
        "Educational Certificates (If Available)",
        "Work Experience Certificates (If Available)",
        "Police Clearance Certificate (PCC)",
        "National Identity Card (NID Card)",
        "Resident Identity Card (For Foreign Residents)",
        "Curriculum Vitae (Europass CV)"
    ]
    
    jobs_high = [
        "MIG & TIG Welders", "Electrical Technicians", "Construction Workers", "Mobile Technicians",
        "Drivers", "RAC Technicians", "Carpenters", "Plumber"
    ]
    
    jobs_medium = [
        "Hotel Staff", "Restaurant Waiters", "Warehouse Workers", "Supermarket Assistants",
        "Factory Workers", "Packing Workers"
    ]
    
    jobs_low = [
        "Delivery Helpers", "Agriculture Workers", "Fruit & Vegetable Picker", "Loading & Unloading Worker",
        "Car Wash Workers", "General Workers", "Cleaners", "Security Guard"
    ]
    
    for c_data in countries_data:
        c_name = c_data["name"]
        slug = slugify(c_name)
        
        # Check files
        flag_path = os.path.join(base_asset_path, f"{c_name.lower()} flag.png")
        if not os.path.exists(flag_path):
             flag_path = os.path.join(base_asset_path, f"{c_name.lower()}  flag.png") # handle typo 'netherland  flag'
             if not os.path.exists(flag_path):
                 flag_path = os.path.join(base_asset_path, f"{c_name.lower()[:10]} flag.png")
        
        cover_path = os.path.join(base_asset_path, f"{c_name.lower()} cover.jpg")
        if not os.path.exists(cover_path):
             cover_path = os.path.join(base_asset_path, f"{c_name.lower()[:10]} cover.jpg")

        # Create Country
        country, created = Country.objects.get_or_create(
            name=c_name,
            defaults={
                "slug": slug,
                "code": c_data["code"],
                "currency": c_data["currency"],
                "language": c_data["language"],
                "processing_time": "Within 190 Days",
                "is_active": True
            }
        )
        
        # Update flag and cover if missing
        if created or not country.flag or not country.image:
            if not country.flag and os.path.exists(flag_path):
                print(f"Uploading flag for {c_name}")
                country.flag = upload_image(flag_path)
            if not country.image and os.path.exists(cover_path):
                print(f"Uploading cover for {c_name}")
                country.image = upload_image(cover_path)
            country.save()
            
        print(f"Country {c_name} prepared.")
        
        # Create Visa
        visa, v_created = Visa.objects.get_or_create(
            country=country,
            category=category,
            name=f"{c_name} Work Permit Visa",
            defaults={
                "slug": slugify(f"{c_name} Work Permit Visa"),
                "description": "After starting employment, the remaining balance may be paid over deductions of 50% from the applicant's monthly salary. 1st Installment: 100% refundable if Document Submission Approval is not received within seven (7) days.",
                "minimum_salary": Decimal("1200"),
                "maximum_salary": Decimal("2500"),
                "minimum_processing_days": 1,
                "maximum_processing_days": 190,
                "duration_in_months": 24, # default 2 yrs
                "from_any_country": True,
                "is_active": True
            }
        )
        print(f"  Visa {visa.name} prepared.")
        
        # Create Requirements
        for i, req in enumerate(requirements):
            VisaRequirement.objects.get_or_create(
                visa=visa,
                title=req,
                defaults={"requirement_type": "Document", "display_order": i, "is_required": True, "is_active": True}
            )
            
        # Create Jobs
        def create_job(title, min_sal, max_sal, benefits):
            VisaJob.objects.get_or_create(
                visa=visa,
                title=title,
                defaults={
                    "minimum_salary": min_sal,
                    "maximum_salary": max_sal,
                    "currency": "EUR",
                    "duty_days_per_week": benefits["days"],
                    "duty_hours_per_day": benefits["hours"],
                    "overtime_available": True,
                    "accommodation": True,
                    "food": False,
                    "medical": True,
                    "transportation": True,
                    "age_requirement": benefits["age"],
                    "is_active": True
                }
            )

        for job in jobs_high:
            create_job(job, Decimal("1900"), Decimal("2500"), {"days": 5, "hours": 8, "age": "18-45 Years"})
        for job in jobs_medium:
            create_job(job, Decimal("1400"), Decimal("1700"), {"days": 6, "hours": 8, "age": "18-45 Years"})
        for job in jobs_low:
            create_job(job, Decimal("1200"), Decimal("1400"), {"days": 6, "hours": 8, "age": "18-50 Years"})
            
    print("Database loading complete.")

if __name__ == "__main__":
    load_data()
