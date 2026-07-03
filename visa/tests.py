from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from country.models import Country
from visa.models import Visa, VisaCategory


class VisaApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_inactive_visa_is_listed(self):
        country = Country.objects.create(
            name="Test Country",
            slug="test-country",
            code="TST",
            currency="USD",
            capital="Test City",
            time_zone="UTC",
            processing_time="1 week",
        )
        category = VisaCategory.objects.create(
            name="Test Category",
            slug="test-category",
        )
        Visa.objects.create(
            country=country,
            category=category,
            name="Inactive Visa",
            slug="inactive-visa",
            is_active=False,
        )

        response = self.client.get(reverse("visa-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["name"], "Inactive Visa")
