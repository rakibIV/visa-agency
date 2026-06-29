from django.contrib.auth import get_user_model
from rest_framework import serializers

from .services import (
    create_staff,
    update_staff,
)
from .models import (
    Designation,
    Staff,
    StaffMonthlySlot,
    StaffDocument,
    StaffEmergencyContact,
)

User = get_user_model()


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = [
            "id",
            "name",
        ]


class StaffMonthlySlotSerializer(serializers.ModelSerializer):
    remaining_slot = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = StaffMonthlySlot
        fields = [
            "id",
            "allocation_month",
            "total_slot",
            "remaining_slot",
        ]


class StaffDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffDocument
        fields = [
            "id",
            "title",
            "file",
            "display_order",
        ]


class StaffEmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffEmergencyContact
        fields = [
            "id",
            "name",
            "relationship",
            "phone",
            "address",
        ]


class StaffSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        source="user.get_full_name",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    designation = serializers.StringRelatedField()

    office = serializers.StringRelatedField()

    reference_staff = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = [
            "employee_id",
            "full_name",
            "email",
            "photo",
            "designation",
            "office",
            "phone",
            "whatsapp",
            "reference_staff",
            "is_active",
        ]

    def get_reference_staff(self, obj):
        if not obj.reference_staff:
            return None

        return {
            "employee_id": obj.reference_staff.employee_id,
            "name": obj.reference_staff.user.get_full_name(),
        }


class StaffCreateUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        source="user.first_name",
        max_length=150,
    )

    last_name = serializers.CharField(
        source="user.last_name",
        max_length=150,
        required=False,
        allow_blank=True,
    )

    email = serializers.EmailField(
        source="user.email",
        required=False,
        allow_blank=True,
    )

    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={
            "input_type": "password",
        },
    )

    employee_id = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = Staff
        fields = [
            "id",
            "employee_id",
            "first_name",
            "last_name",
            "email",
            "password",
            "photo",
            "signature",
            "designation",
            "office",
            "phone",
            "whatsapp",
            "gender",
            "date_of_birth",
            "nationality",
            "father_name",
            "mother_name",
            "nid_number",
            "passport_number",
            "joining_date",
            "reference_staff",
            "is_active",
        ]

    def validate_email(self, value):
        if not value:
            return value

        queryset = User.objects.filter(
            email=value,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.user_id,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def validate(self, attrs):
        if (
            self.instance is None
            and not attrs.get("password")
        ):
            raise serializers.ValidationError(
                {
                    "password": "This field is required."
                }
            )

        return attrs

    def create(self, validated_data):
        user_data = validated_data.pop(
            "user",
            {},
        )

        first_name = user_data.get("first_name")
        last_name = user_data.get(
            "last_name",
            "",
        )
        email = user_data.get(
            "email",
            "",
        )
        password = validated_data.pop("password")

        return create_staff(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            staff_data=validated_data,
        )

    def update(self, instance, validated_data):
        user_data = validated_data.pop(
            "user",
            {},
        )

        first_name = user_data.get(
            "first_name",
            instance.user.first_name,
        )
        last_name = user_data.get(
            "last_name",
            instance.user.last_name,
        )
        email = user_data.get(
            "email",
            instance.user.email,
        )
        password = validated_data.pop(
            "password",
            None,
        )

        return update_staff(
            staff=instance,
            first_name=first_name,
            last_name=last_name,
            email=email,
            new_password=password,
            staff_data=validated_data,
        )


class StaffDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        source="user.get_full_name",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    designation = serializers.StringRelatedField()

    office = serializers.StringRelatedField()

    reference_staff = serializers.SerializerMethodField()

    monthly_slots = StaffMonthlySlotSerializer(
        many=True,
        read_only=True,
    )

    documents = StaffDocumentSerializer(
        many=True,
        read_only=True,
    )

    emergency_contacts = StaffEmergencyContactSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Staff
        fields = [
            "employee_id",
            "full_name",
            "email",
            "photo",
            "signature",
            "designation",
            "office",
            "phone",
            "whatsapp",
            "gender",
            "date_of_birth",
            "nationality",
            "father_name",
            "mother_name",
            "nid_number",
            "passport_number",
            "joining_date",
            "reference_staff",
            "is_active",
            "monthly_slots",
            "documents",
            "emergency_contacts",
            "created_at",
            "updated_at",
        ]

    def get_reference_staff(self, obj):
        if not obj.reference_staff:
            return None

        return {
            "employee_id": obj.reference_staff.employee_id,
            "name": obj.reference_staff.user.get_full_name(),
        }
