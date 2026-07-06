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
        status = ApplicationStatus.objects.create(
            name="New",
            slug="new",
            is_default=True,
        )
        ApplicationStatus.objects.create(
            name="Payment Confirmed",
            slug="payment-confirmed",
        )
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
        rejected_status = ApplicationStatus.objects.create(
            name="Rejected",
            slug="rejected",
            is_final=True,
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
