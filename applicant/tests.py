from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from applicant.models import (
    ApplicantAgreement,
    ApplicantPayment,
    ApplicantRefund,
    AgreementTemplate,
)
from applicant.serializers import AgreementTemplateClauseSerializer
from applicant.services import (
    change_applicant_status,
    create_applicant,
    create_payment,
    update_payment,
)
from country.models import Country
from core.choices import PaymentInstallmentType
from visa.models import Visa, VisaCategory, VisaJob

from .models import ApplicationStatus


class ApplicantPaymentCurrencyFieldsTests(SimpleTestCase):
    def test_payment_model_has_single_currency_and_euro_amount_fields(self):
        self.assertTrue(
            ApplicantPayment._meta.get_field("currency")
        )
        self.assertTrue(
            ApplicantPayment._meta.get_field("euro_amount")
        )


class AgreementTemplateClauseSerializerTests(SimpleTestCase):
    def test_clause_serializer_exposes_multilingual_fields(self):
        serializer = AgreementTemplateClauseSerializer()

        self.assertIn("clause_number", serializer.fields)
        self.assertIn("title_en", serializer.fields)
        self.assertIn("body_en", serializer.fields)
        self.assertIn("title_ar", serializer.fields)
        self.assertIn("body_ar", serializer.fields)
        self.assertIn("title_bn", serializer.fields)
        self.assertIn("body_bn", serializer.fields)


class ApplicantAgreementGenerationTests(TestCase):
    def test_payment_confirmation_generates_default_agreements(self):
        country = Country.objects.create(name="Germany", currency="EUR")
        visa_category = VisaCategory.objects.create(name="Work")
        visa = Visa.objects.create(
            country=country,
            category=visa_category,
            name="Skilled Worker",
        )
        job = VisaJob.objects.create(
            visa=visa,
            title="Software Engineer",
        )
        status, _ = ApplicationStatus.objects.get_or_create(
            slug="new",
            defaults={"name": "New", "is_default": True, "is_active": True},
        )
        status.is_active = True
        status.save()

        p_status, _ = ApplicationStatus.objects.get_or_create(
            slug="payment-confirmed",
            defaults={"name": "Payment Confirmed", "is_active": True},
        )
        p_status.is_active = True
        p_status.save()
        template = AgreementTemplate.objects.create(
            title="Main Agreement",
            code="main-agreement",
            is_active=True,
            is_default=True,
            body="Hello {full_name}",
        )

        applicant = create_applicant(
            full_name="Rahim Ahmed",
            passport_number="A1234567",
            date_of_birth="1990-01-01",
            visa=visa,
            job=job,
            status=status,
            payment_plan_installments=1,
        )

        self.assertFalse(
            ApplicantAgreement.objects.filter(
                applicant=applicant,
                template=template,
            ).exists()
        )
        
        with patch(
            "applicant.services.get_exchange_rate",
            return_value=Decimal("1.0000"),
        ):
            create_payment(
                applicant=applicant,
                payment_date=date.today(),
                payment_method="cash",
                currency="EUR",
                amount="100.00",
                installment_type=PaymentInstallmentType.INITIAL,
            )

        self.assertTrue(
            ApplicantAgreement.objects.filter(
                applicant=applicant,
                template=template,
            ).exists()
        )


class ApplicantAutomaticTriggerTests(TestCase):
    def _create_applicant(self, **overrides):
        country = Country.objects.create(name="Germany", currency="EUR")
        visa_category = VisaCategory.objects.create(name="Work")
        visa = Visa.objects.create(
            country=country,
            category=visa_category,
            name="Skilled Worker",
        )
        job = VisaJob.objects.create(
            visa=visa,
            title="Software Engineer",
        )
        status = ApplicationStatus.objects.create(
            name="New",
            slug="new",
            is_default=True,
        )
        applicant = create_applicant(
            full_name="Rahim Ahmed",
            passport_number="A1234567",
            date_of_birth="1990-01-01",
            visa=visa,
            job=job,
            status=status,
            **overrides,
        )
        return applicant

    def test_first_installment_payment_moves_to_profile_created_cascade(self):
        applicant = self._create_applicant()
        ApplicationStatus.objects.get_or_create(
            name="First Payment Received",
            defaults={"slug": "first-payment-received"},
        )
        ApplicationStatus.objects.get_or_create(
            name="Profile Created",
            defaults={"slug": "profile-created"},
        )
        ApplicationStatus.objects.get_or_create(
            name="Payment Confirmed",
            defaults={"slug": "payment-confirmed"},
        )

        with patch(
            "applicant.services.get_exchange_rate",
            return_value=Decimal("1.0000"),
        ):
            create_payment(
                applicant=applicant,
                payment_date=date.today(),
                payment_method="cash",
                currency="EUR",
                amount="100.00",
                installment_type=PaymentInstallmentType.INITIAL,
            )

        applicant.refresh_from_db()
        self.assertEqual(
            applicant.status.name,
            "Profile Created",
        )

    def test_final_installment_payment_moves_to_payment_confirmed(self):
        applicant = self._create_applicant(
            payment_plan_installments=2,
        )
        ApplicationStatus.objects.get_or_create(
            name="First Payment Received",
            defaults={"slug": "first-payment-received"},
        )
        ApplicationStatus.objects.get_or_create(
            name="Payment Confirmed",
            defaults={"slug": "payment-confirmed"},
        )

        with patch(
            "applicant.services.get_exchange_rate",
            return_value=Decimal("1.0000"),
        ):
            create_payment(
                applicant=applicant,
                payment_date=date.today(),
                payment_method="cash",
                currency="EUR",
                amount="100.00",
                installment_type=PaymentInstallmentType.INITIAL,
            )
            create_payment(
                applicant=applicant,
                payment_date=date.today(),
                payment_method="cash",
                currency="EUR",
                amount="100.00",
                installment_type=PaymentInstallmentType.SECOND,
            )

        applicant.refresh_from_db()
        self.assertEqual(
            applicant.status.name,
            "Payment Confirmed",
        )

    def test_rejected_applicant_creates_refund_if_eligible(self):
        applicant = self._create_applicant()
        rejected_status, _ = ApplicationStatus.objects.get_or_create(
            slug="rejected",
            defaults={"name": "Rejected", "is_final": True, "is_active": True},
        )
        rejected_status.is_active = True
        rejected_status.save()

        with patch(
            "applicant.services.get_exchange_rate",
            return_value=Decimal("1.0000"),
        ):
            create_payment(
                applicant=applicant,
                payment_date=date.today(),
                payment_method="cash",
                currency="EUR",
                amount="100.00",
                installment_type=PaymentInstallmentType.SECOND,
            )

        change_applicant_status(
            applicant=applicant,
            new_status=rejected_status,
            remarks="Rejected by test",
        )

        self.assertTrue(
            ApplicantRefund.objects.filter(
                applicant=applicant,
                generated_from_rejection=True,
            ).exists()
        )


class ManualExchangeRatePaymentTests(TestCase):
    def test_create_payment_with_manual_exchange_rate(self):
        country = Country.objects.create(name="Germany", currency="EUR")
        visa_category = VisaCategory.objects.create(name="Work")
        visa = Visa.objects.create(
            country=country,
            category=visa_category,
            name="Skilled Worker",
        )
        job = VisaJob.objects.create(
            visa=visa,
            title="Software Engineer",
        )
        status = ApplicationStatus.objects.create(
            name="New",
            slug="new",
            is_default=True,
        )
        applicant = create_applicant(
            full_name="Test Applicant",
            passport_number="B9876543",
            date_of_birth="1995-05-05",
            visa=visa,
            job=job,
            status=status,
        )

        # 140,000 BDT at 140 BDT/EUR rate should yield 1000.00 EUR
        payment = create_payment(
            applicant=applicant,
            payment_date=date.today(),
            payment_method="cash",
            currency="BDT",
            amount=Decimal("140000.00"),
            manual_exchange_rate=Decimal("140.00"),
            installment_type=PaymentInstallmentType.INITIAL,
        )

        self.assertEqual(payment.euro_amount, Decimal("1000.00"))

        # Update payment to 140,000 BDT with manual exchange rate of 135 BDT/EUR
        updated_payment = update_payment(
            payment=payment,
            manual_exchange_rate=Decimal("135.00"),
        )
        # 140000 / 135 = 1037.04 EUR
        self.assertEqual(updated_payment.euro_amount, Decimal("1037.04"))

    def test_gbp_payment_with_manual_exchange_rate(self):
        country = Country.objects.create(name="UK", currency="GBP")
        visa_category = VisaCategory.objects.create(name="Work")
        visa = Visa.objects.create(
            country=country,
            category=visa_category,
            name="Tier 2",
        )
        job = VisaJob.objects.create(
            visa=visa,
            title="Nurse",
        )
        status = ApplicationStatus.objects.create(
            name="New",
            slug="new-gbp",
            is_default=True,
        )
        applicant = create_applicant(
            full_name="GBP Applicant",
            passport_number="C1234567",
            date_of_birth="1992-02-02",
            visa=visa,
            job=job,
            status=status,
        )

        # 5,000 GBP at 1.17 EUR/GBP rate should yield 5850.00 EUR
        payment = create_payment(
            applicant=applicant,
            payment_date=date.today(),
            payment_method="cash",
            currency="GBP",
            amount=Decimal("5000.00"),
            manual_exchange_rate=Decimal("1.17"),
            installment_type=PaymentInstallmentType.INITIAL,
        )

        self.assertEqual(payment.euro_amount, Decimal("5850.00"))


class StatusFlowCountingTests(TestCase):
    def test_statuses_after_visa_approved_are_counted_as_approved(self):
        from applicant.selectors import get_approved_status_ids, get_rejected_status_ids

        ApplicationStatus.objects.all().delete()

        st1 = ApplicationStatus.objects.create(name="Documents Submitted", display_order=1, slug="doc-sub")
        st2 = ApplicationStatus.objects.create(name="Visa Approved", display_order=2, slug="visa-approved")
        st3 = ApplicationStatus.objects.create(name="Ticket & Stamping", display_order=3, slug="ticket-stamping")
        st4 = ApplicationStatus.objects.create(name="Passport Handover", display_order=4, slug="passport-handover")
        st_rej = ApplicationStatus.objects.create(name="Rejected", display_order=5, slug="rejected")

        approved_ids = get_approved_status_ids()
        rejected_ids = get_rejected_status_ids()

        self.assertIn(st2.id, approved_ids)
        self.assertIn(st3.id, approved_ids)
        self.assertIn(st4.id, approved_ids)
        self.assertNotIn(st1.id, approved_ids)
        self.assertNotIn(st_rej.id, approved_ids)
        self.assertIn(st_rej.id, rejected_ids)


class ApplicantSerializerPayloadRobustnessTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Germany", currency="EUR")
        self.visa_category = VisaCategory.objects.create(name="Work")
        self.visa = Visa.objects.create(
            country=self.country,
            category=self.visa_category,
            name="Job Visa",
        )
        self.job = VisaJob.objects.create(
            visa=self.visa,
            title="Chef",
        )
        self.status = ApplicationStatus.objects.create(
            name="New",
            slug="new",
            is_default=True,
            is_active=True,
        )

    def test_create_applicant_with_empty_strings_and_json_profile(self):
        from applicant.serializers import ApplicantSerializer

        payload = {
            "full_name": "Karim Hossain",
            "passport_number": " A1234567 ",
            "nid_number": "1990 1234 5678 90",
            "date_of_birth": "1995-05-12T00:00:00.000Z",
            "visa": str(self.visa.id),
            "job": str(self.job.id),
            "secondary_job": "",
            "slot": "null",
            "lawyer": "",
            "agreement": "",
            "status": "",
            "passport_issue_date": "",
            "passport_expiry_date": "null",
            "payment_plan_installments": "2",
            "profile": '{"father_name": "Abul Hossain", "phone": "+880 1712-345678", "email": "", "marital_status": ""}',
            "refund_bank_detail": "",
        }

        serializer = ApplicantSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        applicant = serializer.save()

        self.assertEqual(applicant.full_name, "Karim Hossain")
        self.assertEqual(applicant.passport_number, "A1234567")
        self.assertEqual(applicant.nid_number, "19901234567890")
        self.assertEqual(str(applicant.date_of_birth), "1995-05-12")
        self.assertEqual(applicant.status, self.status)
        self.assertIsNone(applicant.secondary_job)
        self.assertIsNone(applicant.slot)
        self.assertIsNone(applicant.lawyer)
        self.assertIsNone(applicant.passport_issue_date)
        self.assertEqual(applicant.profile.phone, "+8801712345678")
        self.assertEqual(applicant.profile.email, "")



