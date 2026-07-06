from rest_framework import serializers

from country.models import Country
from country.serializers import CountrySerializer

from agency.models import AgencyService
from agency.serializers import AgencyServiceSerializer

from .models import (
    VisaCategory,
    Visa,
    VisaRequirement,
    VisaStep,
    VisaFAQ,
    VisaSEO,
    VisaJob,
    JobFacility,
)


class VisaCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = VisaCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_featured",
        ]


class VisaRequirementSerializer(serializers.ModelSerializer):

    class Meta:
        model = VisaRequirement

        fields = [
            "id",
            "visa",
            "requirement_type",
            "title",
            "description",
            "is_required",
            "display_order",
        ]


class VisaStepSerializer(serializers.ModelSerializer):

    class Meta:
        model = VisaStep

        fields = [
            "id",
            "visa",
            "title",
            "description",
            "display_order",
        ]


class VisaFAQSerializer(serializers.ModelSerializer):

    class Meta:
        model = VisaFAQ

        fields = [
            "id",
            "visa",
            "question",
            "answer",
            "display_order",
        ]


class VisaSEOSerializer(serializers.ModelSerializer):

    class Meta:
        model = VisaSEO

        fields = [
            "visa",
            "meta_title",
            "meta_description",
            "keywords",
            "canonical_url",
            "og_title",
            "og_description",
            "og_image",
        ]


class JobFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobFacility

        fields = [
            "id",
            "job",
            "title",
            "description",
            "display_order",
        ]


class VisaJobSerializer(serializers.ModelSerializer):

    facilities = JobFacilitySerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = VisaJob

        fields = [
            "id",
            "visa",
            "title",
            "description",
            "minimum_salary",
            "maximum_salary",
            "currency",
            "vacancies",
            "experience_required",
            "duty_days_per_week",
            "duty_hours_per_day",
            "overtime_available",
            "overtime_rate",
            "contract_duration_months",
            "location",
            "language_requirement",
            "education_requirement",
            "gender_preference",
            "age_requirement",
            "facilities",
            "display_order",
        ]


class VisaSerializer(serializers.ModelSerializer):

    country = CountrySerializer(
        read_only=True,
    )

    category = VisaCategorySerializer(
        read_only=True,
    )

    services = AgencyServiceSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Visa

        fields = [
            "id",
            "country",
            "category",
            "name",
            "slug",
            "services",
            "minimum_salary",
            "maximum_salary",
            "minimum_processing_days",
            "maximum_processing_days",
            "duration_in_months",
            "is_featured",
        ]


class VisaDetailSerializer(serializers.ModelSerializer):

    country = CountrySerializer(
        read_only=True,
    )

    category = VisaCategorySerializer(
        read_only=True,
    )

    services = AgencyServiceSerializer(
        many=True,
        read_only=True,
    )

    requirements = VisaRequirementSerializer(
        many=True,
        read_only=True,
    )

    steps = VisaStepSerializer(
        many=True,
        read_only=True,
    )

    faqs = VisaFAQSerializer(
        many=True,
        read_only=True,
    )

    seo = VisaSEOSerializer(
        read_only=True,
        allow_null=True,
    )

    jobs = VisaJobSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Visa

        fields = [
            "id",
            "country",
            "category",
            "name",
            "slug",
            "description",
            "services",
            "jobs",
            "minimum_salary",
            "maximum_salary",
            "working_hours_per_week",
            "overtime_available",
            "minimum_processing_days",
            "maximum_processing_days",
            "duration_in_months",
            "from_any_country",
            "requirements",
            "steps",
            "faqs",
            "seo",
            "created_at",
            "updated_at",
        ]


class VisaCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Visa

        fields = [
            "id",
            "country",
            "category",
            "name",
            "slug",
            "description",
            "services",
            "minimum_salary",
            "maximum_salary",
            "working_hours_per_week",
            "overtime_available",
            "minimum_processing_days",
            "maximum_processing_days",
            "duration_in_months",
            "from_any_country",
            "is_featured",
            "is_active",
            "display_order",
        ]
