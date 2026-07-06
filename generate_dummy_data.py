import os
import django
from django.core.management import call_command
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils.text import slugify
from country.models import Country, CountryRequirement, CountryFAQ
from visa.models import VisaCategory, Visa, VisaRequirement, VisaJob, VisaStep, VisaFAQ, JobFacility
from applicant.models import ApplicationStatus, Applicant, ApplicantAddress, ApplicantPayment, ApplicantDocument, ApplicantProfile
from agency.models import Office, CompanyInformation
from staff.models import Designation, Staff

def generate_data():
    print("Generating core models...")
    
    # 1. Countries
    canada, _ = Country.objects.get_or_create(
        name="Canada",
        code="CA",
        defaults={"nationality": "Canadian", "currency": "CAD", "capital": "Ottawa"}
    )

    australia, _ = Country.objects.get_or_create(
        name="Australia",
        code="AU",
        defaults={"nationality": "Australian", "currency": "AUD", "capital": "Canberra"}
    )

    # 2. Visa Categories
    work_visa, _ = VisaCategory.objects.get_or_create(name="Work Visa", defaults={"slug": slugify("Work Visa")})
    study_visa, _ = VisaCategory.objects.get_or_create(name="Student Visa", defaults={"slug": slugify("Student Visa")})

    # 3. Visas
    visa_can, _ = Visa.objects.get_or_create(
        name="Canada PR",
        country=canada,
        category=work_visa,
        defaults={"slug": slugify("Canada PR")}
    )

    visa_aus, _ = Visa.objects.get_or_create(
        name="Australia Subclass 482",
        country=australia,
        category=work_visa,
        defaults={"slug": slugify("Australia Subclass 482")}
    )

    # Nested Country Data
    CountryRequirement.objects.get_or_create(
        country=canada,
        title="Valid Passport",
        defaults={"requirement_type": "DOCUMENT", "description": "At least 6 months validity."}
    )
    CountryFAQ.objects.get_or_create(
        country=canada,
        question="Is English required?",
        defaults={"answer": "Yes, IELTS is usually required."}
    )

    # Nested Visa Data
    VisaRequirement.objects.get_or_create(
        visa=visa_can,
        title="Job Offer",
        defaults={"requirement_type": "DOCUMENT", "description": "Valid job offer from Canadian employer."}
    )
    VisaJob.objects.get_or_create(
        visa=visa_can,
        title="Software Engineer",
        defaults={"description": "Full-stack developer"}
    )
    VisaStep.objects.get_or_create(
        visa=visa_can,
        title="1. Submit Documents",
        defaults={"description": "Upload all required documents online.", "display_order": 1}
    )
    VisaFAQ.objects.get_or_create(
        visa=visa_can,
        question="What is the processing time?",
        defaults={"answer": "Usually 3-6 months."}
    )

    # Grandchild Data (Level 2 Nesting)
    job, _ = VisaJob.objects.get_or_create(
        visa=visa_can,
        title="Software Engineer"
    )
    JobFacility.objects.get_or_create(
        job=job,
        title="Free Accommodation",
        defaults={"description": "Company provides fully furnished apartment."}
    )

    # 4. Application Statuses
    statuses = [
        ("New", 1, True, False),
        ("Processing", 2, False, False),
        ("First Payment Received", 3, False, False),
        ("Profile Created", 4, False, False),
        ("Payment Confirmed", 5, False, False),
        ("Approved", 6, False, True),
        ("Rejected", 7, False, True),
    ]
    for name, order, default, final in statuses:
        ApplicationStatus.objects.get_or_create(
            name=name,
            defaults={
                "slug": slugify(name),
                "display_order": order, 
                "is_active": True, 
                "is_default": default, 
                "is_final": final
            }
        )
        
    # 5. Office & Staff
    company, _ = CompanyInformation.objects.get_or_create(
        company_name="Visa Agency Co",
        defaults={"phone": "01700000000", "address": "123 Main St"}
    )
    hq, _ = Office.objects.get_or_create(
        branch_name="Headquarters",
        defaults={"company": company, "phone": "01700000000", "address": "123 Main St"}
    )
    agent_desig, _ = Designation.objects.get_or_create(name="Agent")
    
    User = get_user_model()
    dummy_user, created = User.objects.get_or_create(username="dummyagent", defaults={"email": "agent@example.com", "first_name": "Dummy", "last_name": "Agent"})
    if created:
        dummy_user.set_password("agent123")
        dummy_user.save()

    dummy_staff, _ = Staff.objects.get_or_create(
        user=dummy_user,
        employee_id="EMP-001",
        defaults={
            "designation": agent_desig,
            "office": hq,
            "phone": "01700000000",
            "gender": "Male",
            "date_of_birth": datetime.date(1990, 1, 1),
            "nationality": "Bangladeshi",
            "joining_date": timezone.now().date(),
        }
    )

    print("Data generated successfully.")
    
    # 6. Dummy Applicant
    from datetime import date
    applicant, _ = Applicant.objects.get_or_create(
        full_name="John Doe",
        passport_number="AB1234567",
        date_of_birth=date(1990, 1, 1),
        visa=visa_can,
        job=job,
        status=ApplicationStatus.objects.first()
    )

    ApplicantProfile.objects.get_or_create(
        applicant=applicant,
        defaults={"father_name": "Richard Doe", "mother_name": "Jane Doe"}
    )

    ApplicantAddress.objects.get_or_create(
        applicant=applicant,
        address_type="PRESENT",
        country=canada,
        defaults={"village": "Downtown", "district": "Toronto"}
    )

    ApplicantPayment.objects.get_or_create(
        applicant=applicant,
        amount=1000.00,
        defaults={
            "installment_type": "INITIAL",
            "payment_date": date.today(),
            "payment_method": "CASH",
            "currency": "USD",
            "exchange_rate": 1.0,
            "euro_amount": 1000.00,
            "payment_number": 1,
            "received_by": dummy_staff
        }
    )

    ApplicantDocument.objects.get_or_create(
        applicant=applicant,
        title="Passport Copy",
        defaults={"document_type": "PASSPORT"}
    )

    print("Dumping data to dummy_data.json...")
    with open('dummy_data.json', 'w', encoding='utf-8') as f:
        call_command(
            'dumpdata', 
            'auth.User',
            'agency.Office',
            'staff.Designation',
            'staff.Staff',
            'country.Country', 
            'country.CountryRequirement',
            'country.CountryFAQ',
            'visa.VisaCategory', 
            'visa.Visa', 
            'visa.VisaRequirement',
            'visa.VisaJob',
            'visa.VisaStep',
            'visa.VisaFAQ',
            'visa.JobFacility',
            'applicant.ApplicationStatus', 
            'applicant.Applicant',
            'applicant.ApplicantProfile',
            'applicant.ApplicantAddress',
            'applicant.ApplicantPayment',
            'applicant.ApplicantDocument',
            indent=4, 
            stdout=f
        )
    print("dummy_data.json created successfully in the root directory.")

if __name__ == '__main__':
    generate_data()
