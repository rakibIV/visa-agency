import os
import django
import sys

# Setup django
sys.path.append('f:/Rakib/Visa Agency Updated/visa-agency')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from country.models import Country
from visa.models import VisaCategory, Visa, VisaRequirement, VisaJob

def populate():
    print("Starting population...")
    # 1. Visa Category
    cat, _ = VisaCategory.objects.get_or_create(
        name="European Work Permit",
        defaults={"description": "European Work Permit & Employment Assistance Program"}
    )
    
    countries_info = [
        {"name": "Portugal", "code": "PT", "duration": 11},
        {"name": "Netherlands", "code": "NL", "duration": 11},
        {"name": "Poland", "code": "PL", "duration": 11},
        {"name": "Bulgaria", "code": "BG", "duration": 8},
        {"name": "Serbia", "code": "RS", "duration": 8},
    ]
    
    requirements = [
        "Valid Passport (Minimum 6 Months Validity)",
        "Passport Size Photograph (White Background)",
        "Educational Certificates (If Available)",
        "Work Experience Certificates (If Available)",
        "Police Clearance Certificate (PCC)",
        "National Identity Card (NID Card)",
        "Resident Identity Card (For Foreign Residents)",
        "Curriculum Vitae (Europass CV)",
    ]
    
    jobs_data = [
        {
            "category": "High-Demand & Skilled Positions",
            "titles": ["MIG & TIG Welders", "Electrical Technicians", "Construction Workers", "Mobile Technicians", "Drivers", "RAC Technicians", "Carpenters", "Plumber"],
            "min_salary": 1900, "max_salary": 2500,
            "age": "18-45 Years", "days": 5, "hours": 8.0,
        },
        {
            "category": "Medium-Demand & Semi-Skilled Positions",
            "titles": ["Hotel Staff", "Restaurant Waiters", "Warehouse Workers", "Supermarket Assistants", "Factory Workers", "Packing Workers"],
            "min_salary": 1400, "max_salary": 1700,
            "age": "18-45 Years", "days": 6, "hours": 8.0,
        },
        {
            "category": "Entry-Level & Low-Skilled Positions",
            "titles": ["Delivery Helpers", "Agriculture Workers", "Fruit & Vegetable Picker", "Loading & Unloading Worker", "Car Wash Workers", "General Workers", "Cleaners", "Security Guard"],
            "min_salary": 1200, "max_salary": 1400,
            "age": "18-50 Years", "days": 6, "hours": 8.0,
        }
    ]
    
    for c_info in countries_info:
        country, _ = Country.objects.get_or_create(
            name=c_info["name"],
            defaults={"code": c_info["code"], "currency": "EUR", "processing_time": "WITHIN 190 DAYS"}
        )
        
        description = f"""Processing Fee: Only € 2,900
After starting employment in {c_info['name']}, the remaining balance may be paid over {c_info['duration']} months through deductions of 50% from the applicant's monthly salary.
1st Installment: 100% refundable if Document Submission Approval is not received within seven (7) days.
An officially authorized agreement bearing the official seal of AL-RAIYAN GROUP (Kingdom of Saudi Arabia) shall be executed.
All visa processing services shall be managed directly by AL-RAIYAN GROUP (Kingdom of Saudi Arabia)."""
        
        visa_slug = f"{c_info['name'].lower()}-work-permit-visa"
        try:
            visa = Visa.objects.get(slug=visa_slug)
            visa.country = country
            visa.category = cat
            visa.name = "Work Permit Visa"
            visa.description = description.strip()
            visa.minimum_processing_days = 190
            visa.maximum_processing_days = 190
            visa.save()
        except Visa.DoesNotExist:
            visa = Visa.objects.create(
                country=country,
                category=cat,
                name="Work Permit Visa",
                description=description.strip(),
                minimum_processing_days=190,
                maximum_processing_days=190,
                slug=visa_slug
            )
        
        # Add Requirements
        for i, req in enumerate(requirements):
            VisaRequirement.objects.get_or_create(
                visa=visa,
                requirement_type="DOCUMENT",
                title=req,
                defaults={
                    "display_order": i
                }
            )
            
        # Add Jobs
        for job_cat in jobs_data:
            for i, title in enumerate(job_cat["titles"]):
                VisaJob.objects.get_or_create(
                    visa=visa,
                    title=title,
                    defaults={
                        "minimum_salary": job_cat["min_salary"],
                        "maximum_salary": job_cat["max_salary"],
                        "currency": "EUR",
                        "duty_days_per_week": job_cat["days"],
                        "duty_hours_per_day": job_cat["hours"],
                        "overtime_available": True,
                        "accommodation": True,
                        "medical": True,
                        "transportation": True,
                        "food": False,
                        "age_requirement": job_cat["age"],
                        "description": f"Category: {job_cat['category']}"
                    }
                )

if __name__ == "__main__":
    populate()
    print("Database populated successfully from PDF data.")
