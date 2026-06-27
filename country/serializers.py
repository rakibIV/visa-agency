from rest_framework import serializers

from .models import (
    Country,
    CountryRequirement,
    CountryFAQ,
    CountryGallery,
    CountrySEO,
)


class CountryRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryRequirement
        fields = [
            "id",
            "requirement_type",
            "title",
            "description",
            "display_order",
        ]


class CountryFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryFAQ
        fields = [
            "id",
            "question",
            "answer",
            "display_order",
        ]


class CountryGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryGallery
        fields = [
            "id",
            "image",
            "caption",
            "display_order",
        ]


class CountrySEOSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountrySEO
        fields = [
            "meta_title",
            "meta_description",
            "meta_keywords",
            "canonical_url",
            "schema_markup",
        ]


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            "id",
            "name",
            "slug",
            "flag",
            "featured_image",
            "currency",
            "language",
            "processing_time",
            "featured_image",
            "capital",
            "currency",
            "language",
            "processing_time",
            "visa_required",
            "time_zone",
        ]


class CountryDetailSerializer(serializers.ModelSerializer):
    requirements = CountryRequirementSerializer(
        many=True,
        read_only=True,
    )

    faqs = CountryFAQSerializer(
        many=True,
        read_only=True,
    )

    gallery = CountryGallerySerializer(
        many=True,
        read_only=True,
    )

    seo = CountrySEOSerializer(
        read_only=True,
    )

    class Meta:
        model = Country
        fields = [
            "id",
            "name",
            "slug",
            "flag",
            "featured_image",
            "short_description",
            "description",
            "capital",
            "currency",
            "language",
            "time_zone",
            "visa_required",
            "processing_time",
            "requirements",
            "gallery",
            "faqs",
            "seo",
            "created_at",
            "updated_at",
        ]