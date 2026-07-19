import os
import django
import sys

sys.path.append('f:/Rakib/Visa Agency Updated/visa-agency')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from country.models import Country, CountryRequirement, CountryFAQ

def populate():
    print("Starting Country Details Population...")
    
    countries_info = [
        {"name": "Portugal", "duration": 11},
        {"name": "Netherlands", "duration": 11},
        {"name": "Poland", "duration": 11},
        {"name": "Bulgaria", "duration": 8},
        {"name": "Serbia", "duration": 8},
    ]
    
    requirements = [
        ("Valid Passport", "Minimum 6 Months Validity required for the application process."),
        ("Passport Size Photograph", "Must be taken with a clear white background."),
        ("Educational Certificates", "Provide certificates if available. Higher education improves approval chances."),
        ("Work Experience Certificates", "Provide certificates if available. Relevant experience makes your application stand out!"),
        ("Police Clearance Certificate (PCC)", "A must-have for background verification. Ensure it is recent."),
        ("National Identity Card (NID Card)", "Your official state-issued ID card."),
        ("Resident Identity Card", "Only applicable if you are currently residing in a foreign country."),
        ("Curriculum Vitae", "Must be in the Europass CV format highlighting all skills and experiences."),
    ]
    
    for c_info in countries_info:
        try:
            country = Country.objects.get(name=c_info["name"])
        except Country.DoesNotExist:
            print(f"Country {c_info['name']} not found, skipping...")
            continue
            
        # 1. Update Description (Tricky/Engaging Info)
        html_desc = f"""
        <p><strong>A golden opportunity</strong> to work legally in <strong>{c_info['name']}</strong> and potentially obtain long-term residence with your family! We undertake full responsibility for processing your European Work Permit Visa application.</p>
        
        <h3>Flexible Payment Facility</h3>
        <p>You don't need to pay everything upfront! The processing fee is <strong>only € 2,900</strong>. After starting employment in {c_info['name']}, the remaining balance may be paid over <strong>{c_info['duration']} months</strong> through monthly installments deducted directly from your salary.</p>
        
        <p><em>Disclaimer: Final approval of work permits, visas, and employment contracts is subject to the decisions of the respective employers, immigration authorities, and the Embassy of {c_info['name']}.</em></p>
        """
        
        country.description = html_desc.strip()
        country.save()
        
        # 2. Add Country Requirements
        for i, (title, desc) in enumerate(requirements):
            CountryRequirement.objects.get_or_create(
                country=country,
                requirement_type="DOCUMENT",
                title=title,
                defaults={
                    "description": desc,
                    "display_order": i
                }
            )
            
        # 3. Add FAQs
        faqs = [
            ("What is the total processing fee?", "The processing fee is highly competitive at only € 2,900."),
            ("How does the flexible payment facility work?", f"You can pay the remaining balance in monthly installments directly from your salary after you commence employment. For {c_info['name']}, this deduction spans over {c_info['duration']} months."),
            ("Is the first installment refundable?", "Yes! Your 1st installment is 100% refundable if your Document Submission Approval is not received within seven (7) days."),
            ("How long does the visa processing take?", "The estimated processing time is within 190 days from the date of your complete document submission."),
            ("What are the age limits?", "We accept applications for candidates generally between 18 to 45 years for high/medium skilled jobs, and up to 50 years for entry-level positions."),
        ]
        
        for i, (q, a) in enumerate(faqs):
            CountryFAQ.objects.get_or_create(
                country=country,
                question=q,
                defaults={
                    "answer": a,
                    "display_order": i
                }
            )
            
    print("Country details populated successfully.")

if __name__ == "__main__":
    populate()
