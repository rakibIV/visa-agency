from rest_framework import serializers

from .models import (
    AgreementTemplate,
    ApplicantAddress,
    ApplicantProfile,
    ApplicantTag,
    ApplicationStatus,
    ApplicantDocument,
    ApplicantNote,
    ApplicantPayment,
    ApplicantStatusHistory,
    Applicant,
)

from .services import (
    add_note,
    create_applicant_address,
    create_applicant,
    create_payment,
    update_applicant_address,
    update_applicant,
    update_document,
    update_note,
    update_payment,
    upload_document,
)


# ==========================================================
# Lookup Serializers
# ==========================================================

class ApplicationStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicationStatus

        fields = (
            "id",
            "name",
            "slug",
            "description",
            "color",
            "is_default",
            "is_final",
            "display_order",
        )

        read_only_fields = (
            "id",
        )


class ApplicantTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicantTag

        fields = (
            "id",
            "name",
            "color",
        )

        read_only_fields = (
            "id",
        )


class AgreementTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AgreementTemplate

        fields = (
            "id",
            "title",
            "visa",
            "body",
            "version",
            "is_active",
        )

        read_only_fields = (
            "id",
        )


# ==========================================================
# Applicant Profile
# ==========================================================

class ApplicantProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicantProfile

        fields = (
            "id",
            "father_name",
            "mother_name",
            "phone",
            "email",
            "occupation",
            "marital_status",
            "gender",
            "nationality",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relation",
        )

        read_only_fields = (
            "id",
        )


# ==========================================================
# Applicant Address
# ==========================================================

class ApplicantAddressSerializer(serializers.ModelSerializer):

    country_name = serializers.CharField(
        source="country.name",
        read_only=True,
    )

    class Meta:
        model = ApplicantAddress

        fields = (
            "id",
            "address_type",
            "village",
            "post_office",
            "police_station",
            "district",
            "country",
            "country_name",
            "extra_fields",
        )

        read_only_fields = (
            "id",
        )

    def create(self, validated_data):

        applicant = validated_data.pop(
            "applicant",
        )

        return create_applicant_address(
            applicant=applicant,
            **validated_data,
        )

    def update(self, instance, validated_data):

        validated_data.pop(
            "applicant",
            None,
        )

        return update_applicant_address(
            applicant_address=instance,
            **validated_data,
        )



# ==========================================================
# Applicant Payment
# ==========================================================

class ApplicantPaymentSerializer(serializers.ModelSerializer):

    applicant_name = serializers.CharField(
        source="applicant.full_name",
        read_only=True,
    )

    application_id = serializers.CharField(
        source="applicant.application_id",
        read_only=True,
    )

    received_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ApplicantPayment

        fields = (
            "id",
            "applicant",
            "application_id",
            "applicant_name",
            "payment_number",
            "payment_date",
            "payment_method",
            "currency",
            "amount",
            "exchange_rate",
            "euro_amount",
            "received_by",
            "received_by_name",
            "note",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "payment_number",
            "euro_amount",
            "created_at",
            "updated_at",
        )

    def get_received_by_name(self, obj):

        if obj.received_by:
            return obj.received_by.user.get_full_name()

        return None

    def create(self, validated_data):

        return create_payment(
            **validated_data,
        )

    def update(self, instance, validated_data):

        validated_data.pop(
            "applicant",
            None,
        )

        return update_payment(
            payment=instance,
            **validated_data,
        )


# ==========================================================
# Applicant Document
# ==========================================================

class ApplicantDocumentSerializer(serializers.ModelSerializer):

    applicant_name = serializers.CharField(
        source="applicant.full_name",
        read_only=True,
    )

    verified_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ApplicantDocument

        fields = (
            "id",
            "applicant",
            "applicant_name",
            "document_type",
            "file",
            "verified",
            "verified_by",
            "verified_by_name",
            "verified_at",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "verified",
            "verified_by",
            "verified_by_name",
            "verified_at",
            "created_at",
            "updated_at",
        )

    def get_verified_by_name(self, obj):

        if obj.verified_by:
            return obj.verified_by.user.get_full_name()

        return None

    def create(self, validated_data):

        return upload_document(
            **validated_data,
        )

    def update(self, instance, validated_data):

        validated_data.pop(
            "applicant",
            None,
        )

        return update_document(
            document=instance,
            **validated_data,
        )


# ==========================================================
# Applicant Note
# ==========================================================

class ApplicantNoteSerializer(serializers.ModelSerializer):

    applicant_name = serializers.CharField(
        source="applicant.full_name",
        read_only=True,
    )

    staff_name = serializers.SerializerMethodField()

    class Meta:
        model = ApplicantNote

        fields = (
            "id",
            "applicant",
            "applicant_name",
            "staff",
            "staff_name",
            "note",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def get_staff_name(self, obj):

        return obj.staff.user.get_full_name()

    def create(self, validated_data):

        return add_note(
            **validated_data,
        )

    def update(self, instance, validated_data):

        validated_data.pop(
            "applicant",
            None,
        )

        return update_note(
            applicant_note=instance,
            **validated_data,
        )


# ==========================================================
# Applicant Status History
# ==========================================================

class ApplicantStatusHistorySerializer(serializers.ModelSerializer):

    applicant_name = serializers.CharField(
        source="applicant.full_name",
        read_only=True,
    )

    old_status_name = serializers.CharField(
        source="old_status.name",
        read_only=True,
    )

    new_status_name = serializers.CharField(
        source="new_status.name",
        read_only=True,
    )

    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ApplicantStatusHistory

        fields = (
            "id",
            "applicant",
            "applicant_name",
            "old_status",
            "old_status_name",
            "new_status",
            "new_status_name",
            "remarks",
            "changed_by",
            "changed_by_name",
            "created_at",
        )

        read_only_fields = (
            "id",
            "created_at",
        )

    def get_changed_by_name(self, obj):

        if obj.changed_by:
            return obj.changed_by.user.get_full_name()

        return None
# ==========================================================
# Applicant List Serializer
# ==========================================================

class ApplicantListSerializer(serializers.ModelSerializer):

    visa_name = serializers.CharField(
        source="visa.name",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="status.name",
        read_only=True,
    )

    assigned_staff_name = serializers.SerializerMethodField()

    class Meta:
        model = Applicant

        fields = (
            "id",
            "application_id",
            "full_name",
            "photo",
            "passport_number",
            "visa",
            "visa_name",
            "status",
            "status_name",
            "assigned_staff",
            "assigned_staff_name",
            "created_at",
        )

        read_only_fields = (
            "id",
            "application_id",
            "created_at",
        )

    def get_assigned_staff_name(self, obj):

        if obj.assigned_staff:
            return obj.assigned_staff.user.get_full_name()

        return None


# ==========================================================
# Applicant Create / Update Serializer
# ==========================================================

class ApplicantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Applicant

        exclude = (
            "deleted_at",
            "is_deleted",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "application_id",
            "created_by",
            "updated_by",
        )

    def create(self, validated_data):

        return create_applicant(
            **validated_data,
        )

    def update(
        self,
        instance,
        validated_data,
    ):

        return update_applicant(
            applicant=instance,
            **validated_data,
        )


# ==========================================================
# Applicant Detail Serializer
# ==========================================================

class ApplicantDetailSerializer(serializers.ModelSerializer):

    status = ApplicationStatusSerializer(
        read_only=True,
    )

    agreement = AgreementTemplateSerializer(
        read_only=True,
    )

    profile = ApplicantProfileSerializer(
        read_only=True,
    )

    addresses = ApplicantAddressSerializer(
        many=True,
        read_only=True,
    )

    payments = ApplicantPaymentSerializer(
        many=True,
        read_only=True,
    )

    documents = ApplicantDocumentSerializer(
        many=True,
        read_only=True,
    )

    notes = ApplicantNoteSerializer(
        many=True,
        read_only=True,
    )

    status_history = ApplicantStatusHistorySerializer(
        many=True,
        read_only=True,
    )

    tags = ApplicantTagSerializer(
        many=True,
        read_only=True,
    )

    visa_name = serializers.CharField(
        source="visa.name",
        read_only=True,
    )

    slot_month = serializers.DateField(
        source="slot.allocation_month",
        read_only=True,
    )

    assigned_staff_name = serializers.SerializerMethodField()

    class Meta:
        model = Applicant

        fields = (
            "id",
            "application_id",
            "full_name",
            "photo",
            "passport_number",
            "passport_issue_date",
            "passport_expiry_date",
            "nid_number",
            "date_of_birth",
            "place_of_birth",
            "current_country",
            "visa",
            "visa_name",
            "status",
            "slot",
            "slot_month",
            "assigned_staff",
            "assigned_staff_name",
            "agreement",
            "tags",
            "profile",
            "addresses",
            "payments",
            "documents",
            "notes",
            "status_history",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_assigned_staff_name(self, obj):

        if obj.assigned_staff:
            return obj.assigned_staff.user.get_full_name()

        return None
