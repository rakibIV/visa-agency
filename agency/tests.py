from django.test import TestCase

from .models import ContactUs, Notice, Review


class NoticeModelTests(TestCase):
    def test_notice_slug_is_generated_from_title(self):
        notice = Notice.objects.create(title="Important Update")

        self.assertEqual(notice.slug, "important-update")
        self.assertTrue(notice.is_active)


class ReviewModelTests(TestCase):
    def test_review_defaults_to_active_and_generous_rating(self):
        review = Review.objects.create(
            name="Amina Rahman",
            comment="Wonderful service and very helpful team.",
        )

        self.assertTrue(review.is_active)
        self.assertEqual(review.rating, 5)


class ContactUsModelTests(TestCase):
    def test_contact_message_defaults_to_unread(self):
        contact = ContactUs.objects.create(
            name="Karim",
            email="karim@example.com",
            subject="Visa consultation",
            message="I would like to know more about the process.",
        )

        self.assertFalse(contact.is_read)
        self.assertTrue(contact.is_active)
