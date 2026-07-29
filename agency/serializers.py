from rest_framework import serializers

from .models import (
    AgencyService,
    CompanyInformation,
    ContactUs,
    Office,
    SocialLink,
    EmailTemplate,
    Lawyer,
    Notice,
    Review,
    ApplicationRequest,
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
            "is_active",
        ]


class NoticeSerializer(serializers.ModelSerializer):
    attachment = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "attachment",
            "is_pinned",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "name",
            "comment",
            "rating",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "subject",
            "message",
            "is_read",
            "is_active",
            "created_at",
            "updated_at",
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
            "is_active",
        ]
        read_only_fields = ["company"]


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
            "is_active",
        ]
        read_only_fields = ["company"]


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
            "is_generous",
            "top_left_logo",
            "top_center_logo",
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
            "smtp_password",
            "phone",
            "address",
            "country",
            "country_name",
            "is_default",
            "is_active",
        ]


class CompanyInformationSerializer(serializers.ModelSerializer):
    company_logo = serializers.ImageField(
        required=False,
        allow_null=True,
    )
    favicon = serializers.ImageField(
        required=False,
        allow_null=True,
    )
    company_signature = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = CompanyInformation
        fields = [
            "id",
            "company_name",
            "company_logo",
            "favicon",
            "company_signature",
            "tagline",
            "money_receipt_important_note",
            "phone",
            "whatsapp",
            "email",
            "website",
            "address",
            "about",
            "mission",
            "vision",
            "is_active",
        ]


class CompanyInformationDetailSerializer(serializers.ModelSerializer):
    company_logo = serializers.ImageField(
        required=False,
        allow_null=True,
    )
    favicon = serializers.ImageField(
        required=False,
        allow_null=True,
    )
    company_signature = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    branches = OfficeSerializer(
        many=True,
        read_only=True,
    )

    social_links = SocialLinkSerializer(
        many=True,
        read_only=True,
    )

    images = serializers.SerializerMethodField()
    logos = serializers.SerializerMethodField()

    def get_images(self, obj):
        from .serializers import AgencyImageSerializer
        return AgencyImageSerializer(obj.images.all(), many=True, context=self.context).data

    def get_logos(self, obj):
        from .serializers import CompanyLogoSerializer
        return CompanyLogoSerializer(obj.logos.filter(is_active=True).order_by('serial_number'), many=True, context=self.context).data

    class Meta:
        model = CompanyInformation
        fields = [
            "id",
            "company_name",
            "company_logo",
            "favicon",
            "company_signature",
            "tagline",
            "money_receipt_important_note",
            "phone",
            "whatsapp",
            "email",
            "website",
            "address",
            "about",
            "mission",
            "vision",
            "is_active",
            "branches",
            "social_links",
            "images",
            "logos",
            "created_at",
            "updated_at",
        ]





class ApplicationRequestSerializer(serializers.ModelSerializer):
    target_visa_name = serializers.CharField(source='target_visa.name', read_only=True)
    target_country_name = serializers.CharField(source='target_visa.country.name', read_only=True)

    class Meta:
        model = ApplicationRequest
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "message",
            "target_visa",
            "target_visa_name",
            "target_country_name",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "name",
            "comment",
            "rating",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "subject",
            "message",
            "is_read",
            "is_active",
            "created_at",
            "updated_at",
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
            "is_active",
        ]
        read_only_fields = ["company"]


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
            "is_active",
        ]
        read_only_fields = ["company"]


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
            "is_generous",
            "top_left_logo",
            "top_center_logo",
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
            "smtp_password",
            "phone",
            "address",
            "country",
            "country_name",
            "is_default",
            "is_active",
        ]





class ApplicationRequestSerializer(serializers.ModelSerializer):
    target_visa_name = serializers.CharField(source='target_visa.name', read_only=True)
    target_country_name = serializers.CharField(source='target_visa.country.name', read_only=True)

    class Meta:
        model = ApplicationRequest
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "message",
            "target_visa",
            "target_visa_name",
            "target_country_name",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            'id',
            'created_at',
            'updated_at',
        )

class AgencyImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)

    class Meta:
        from .models import AgencyImage
        model = AgencyImage
        fields = '__all__'


class CompanyLogoSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    company_name = serializers.CharField(source="company.company_name", read_only=True)

    class Meta:
        from .models import CompanyLogo
        model = CompanyLogo
        fields = [
            "id",
            "company",
            "company_name",
            "title",
            "serial_number",
            "image",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ImportantNoteSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.company_name", read_only=True)

    class Meta:
        from .models import ImportantNote
        model = ImportantNote
        fields = [
            "id",
            "company",
            "company_name",
            "title",
            "content",
            "is_default",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


