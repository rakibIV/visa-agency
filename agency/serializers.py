from rest_framework import serializers

from .models import (
    AgencyService,
    CompanyInformation,
    Office,
    SocialLink,
    EmailTemplate,
    Lawyer,
)


class AgencyServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyService
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "icon",
            "is_featured",
            "display_order",
        ]


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = [
            "id",
            "company",
            "branch_name",
            "email",
            "phone",
            "address",
            "office_hours",
            "is_head_office",
            "display_order",
        ]


class SocialLinkSerializer(serializers.ModelSerializer):

    platform_name = serializers.CharField(
        source="get_platform_display",
        read_only=True,
    )

    class Meta:
        model = SocialLink
        fields = [
            "id",
            "company",
            "platform",
            "platform_name",
            "url",
            "display_order",
        ]


class EmailTemplateSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(
        source="status.name",
        read_only=True,
    )

    class Meta:
        model = EmailTemplate
        fields = [
            "id",
            "name",
            "status",
            "status_name",
            "subject",
            "body",
            "is_active",
        ]


class LawyerSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(
        source="country.name",
        read_only=True,
    )

    class Meta:
        model = Lawyer
        fields = [
            "id",
            "name",
            "email",
            "env_key",
            "phone",
            "country",
            "country_name",
            "is_default",
            "is_active",
        ]


class CompanyInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInformation
        fields = [
            "id",
            "company_name",
            "company_logo",
            "favicon",
            "phone",
        ]


class CompanyInformationDetailSerializer(serializers.ModelSerializer):

    branches = OfficeSerializer(
        many=True,
        read_only=True,
    )

    social_links = SocialLinkSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = CompanyInformation
        fields = [
            "id",
            "company_name",
            "company_logo",
            "favicon",
            "phone",
            "address",
            "about",
            "mission",
            "vision",
            "branches",
            "social_links",
            "created_at",
            "updated_at",
        ]
