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
            "country",
            "requirement_type",
            "title",
            "description",
            "display_order",
        ]
        read_only_fields = ["country"]


class CountryFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryFAQ
        fields = [
            "id",
            "country",
            "question",
            "answer",
            "display_order",
        ]
        read_only_fields = ["country"]


class CountryGallerySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CountryGallery
        fields = [
            "id",
            "country",
            "image",
            "caption",
            "display_order",
        ]
        read_only_fields = ["country"]


class CountrySEOSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountrySEO
        fields = [
            "meta_title",
            "country",
            "meta_description",
            "meta_keywords",
            "canonical_url",
        ]
        read_only_fields = ["country"]


class CountrySerializer(serializers.ModelSerializer):
    flag = serializers.ImageField(required=False, allow_null=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Country
        fields = [
            "id",
            "name",
            "slug",
            "flag",
            "image",
            "is_featured",
            "currency",
            "language",
            "processing_time",
            "capital",
            "time_zone",
            "short_description",
            "is_active",
        ]


class CountryDetailSerializer(serializers.ModelSerializer):
    flag = serializers.ImageField(required=False, allow_null=True)
    image = serializers.ImageField(required=False, allow_null=True)
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
        allow_null=True,
    )

    class Meta:
        model = Country
        fields = [
            "id",
            "name",
            "slug",
            "flag",
            "image",
            "is_featured",
            "short_description",
            "description",
            "capital",
            "currency",
            "language",
            "time_zone",
            "processing_time",
            "requirements",
            "gallery",
            "faqs",
            "seo",
            "created_at",
            "updated_at",
        ]