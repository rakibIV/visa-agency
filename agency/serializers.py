from rest_framework import serializers

from .models import (
    AgencyService,
    CompanyInformation,
    Office,
    SocialLink,
    EmailTemplate,
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
            "office_name",
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
            "platform",
            "platform_name",
            "url",
            "display_order",
        ]


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = [
            "id",
            "name",
            "subject",
            "body",
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

    offices = OfficeSerializer(
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
            "offices",
            "social_links",
            "created_at",
            "updated_at",
        ]