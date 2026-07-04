from rest_framework import serializers

from agency.models import (
    Lawyer,
    EmailTemplate as AgencyEmailTemplate,
)

from .models import (
    AgreementTemplate,
    AgreementTemplateClause,
    ApplicantAddress,
    ApplicantProfile,
    ApplicantTag,
    ApplicationStatus,
    ApplicantDocument,
    ApplicantMoneyReceipt,
    ApplicantNote,
    ApplicantPayment,
    ApplicantRefund,
    ApplicantRefundBankDetail,
    ApplicantRefundReceipt,
    ApplicantStatusHistory,
    CurrencyRate,
    Applicant,
)

from .services import (
    add_note,
    create_applicant_address,
    create_applicant,
    create_payment,
    create_or_update_applicant_refund_bank_detail,
    create_refund_for_rejected_applicant,
    generate_money_receipt_for_payment,
    generate_refund_receipt_for_applicant,
    get_applicant_payment_summary,
    calculate_refund_breakdown,
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
            "body",
            "version",
            "is_active",
        )

        read_only_fields = (
            "id",
        )


class AgreementTemplateClauseSerializer(serializers.ModelSerializer):

    class Meta:
        model = AgreementTemplateClause

        fields = (
            "id",
            "template",
            "clause_key",
            "clause_number",
            "title_en",
            "title_ar",
            "title_bn",
            "body_en",
            "body_ar",
            "body_bn",
            "visibility_mode",
            "countries",
            "visibility_rules",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "clause_key",
            "created_at",
            "updated_at",
        )


class MailTriggerSerializer(serializers.Serializer):

    applicant_id = serializers.PrimaryKeyRelatedField(
        queryset=Applicant.objects.filter(
            is_deleted=False,
        ),
        write_only=True,
    )

    template_id = serializers.PrimaryKeyRelatedField(
        queryset=AgencyEmailTemplate.objects.filter(
            is_active=True,
        ),
        write_only=True,
    )

    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=Lawyer.objects.filter(
            is_active=True,
        ),
        write_only=True,
    )

    def validate(self, attrs):
        attrs["applicant"] = attrs.pop("applicant_id")
        attrs["template"] = attrs.pop("template_id")
        attrs["sender"] = attrs.pop("sender_id")
        return attrs


class ApplicantStatusEmailUpdateSerializer(serializers.Serializer):

    new_status = serializers.PrimaryKeyRelatedField(
        source="status",
        queryset=ApplicationStatus.objects.filter(
            is_active=True,
        ),
    )

    sender = serializers.PrimaryKeyRelatedField(
        queryset=Lawyer.objects.filter(
            is_active=True,
        ),
        required=False,
        allow_null=True,
    )

    send_email = serializers.BooleanField(
        required=False,
        default=False,
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


class ApplicantManualEmailSerializer(serializers.Serializer):

    sender = serializers.PrimaryKeyRelatedField(
        queryset=Lawyer.objects.filter(
            is_active=True,
        ),
    )

    template = serializers.PrimaryKeyRelatedField(
        queryset=AgencyEmailTemplate.objects.filter(
            is_active=True,
        ),
    )


# =========================================================
# Currency Rates
# =========================================================

class CurrencyRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CurrencyRate

        fields = (
            "id",
            "base_currency",
            "target_currency",
            "rate",
            "source",
            "fetched_at",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


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

    currency_rate_info = CurrencyRateSerializer(
        source="currency_rate",
        read_only=True,
    )

    class Meta:
        model = ApplicantPayment

        fields = (
            "id",
            "applicant",
            "application_id",
            "applicant_name",
            "currency_rate",
            "currency_rate_info",
            "payment_number",
            "installment_type",
            "receipt_number",
            "payment_date",
            "payment_method",
            "currency",
            "amount",
            "exchange_rate",
            "euro_amount",
            "reference",
            "received_by",
            "received_by_name",
            "note",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "currency_rate",
            "payment_number",
            "exchange_rate",
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


class ApplicantMoneyReceiptSerializer(serializers.ModelSerializer):

    applicant_name = serializers.CharField(
        source="applicant.full_name",
        read_only=True,
    )

    application_id = serializers.CharField(
        source="applicant.application_id",
        read_only=True,
    )

    generated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ApplicantMoneyReceipt

        fields = (
            "id",
            "applicant",
            "application_id",
            "applicant_name",
            "payment",
            "receipt_number",
            "receipt_type",
            "payment_reference",
            "installment_type",
            "installment_label",
            "payment_number",
            "payment_date",
            "payment_method",
            "currency",
            "amount",
            "exchange_rate",
            "euro_amount",
            "applicant_snapshot",
            "staff_snapshot",
            "visa_job_country_snapshot",
            "payment_snapshot",
            "summary_text",
            "notes",
            "generated_by",
            "generated_by_name",
            "generated_at",
            "is_void",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_generated_by_name(self, obj):
        if obj.generated_by:
            return obj.generated_by.get_full_name()

        return None


class GenerateMoneyReceiptSerializer(serializers.Serializer):

    payment = serializers.PrimaryKeyRelatedField(
        queryset=ApplicantPayment.objects.all(),
    )

    force_new = serializers.BooleanField(
        required=False,
        default=False,
    )

    def validate_payment(self, payment):
        applicant = self.context.get(
            "applicant",
        )

        if applicant and payment.applicant_id != applicant.id:
            raise serializers.ValidationError(
                "Payment does not belong to this applicant."
            )

        return payment

    def save(self, **kwargs):
        user = self.context.get(
            "user",
        )

        return generate_money_receipt_for_payment(
            self.validated_data["payment"],
            generated_by=user if getattr(user, "is_authenticated", False) else None,
            force_new=self.validated_data.get(
                "force_new",
                False,
            ),
        )


class ApplicantRefundBankDetailSerializer(serializers.ModelSerializer):

    applicant_name = serializers.CharField(
        source="applicant.full_name",
        read_only=True,
    )

    class Meta:
        model = ApplicantRefundBankDetail

        fields = (
            "id",
            "applicant",
            "applicant_name",
            "account_holder_name",
            "bank_name",
            "branch_name",
            "district_name",
            "account_number_or_iban",
            "routing_number",
            "mobile_number",
            "country",
            "notes",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "applicant",
            "applicant_name",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        return create_or_update_applicant_refund_bank_detail(
            **validated_data,
        )

    def update(self, instance, validated_data):
        validated_data.pop(
            "applicant",
            None,
        )

        return create_or_update_applicant_refund_bank_detail(
            applicant=instance.applicant,
            **validated_data,
        )


class ApplicantRefundSerializer(serializers.ModelSerializer):

    applicant_name = serializers.CharField(
        source="applicant.full_name",
        read_only=True,
    )

    application_id = serializers.CharField(
        source="applicant.application_id",
        read_only=True,
    )

    receipt_count = serializers.IntegerField(
        source="receipts.count",
        read_only=True,
    )

    class Meta:
        model = ApplicantRefund

        fields = (
            "id",
            "applicant",
            "application_id",
            "applicant_name",
            "refund_status",
            "refund_type",
            "refund_basis",
            "refund_percentage",
            "refundable_payment_total",
            "refund_amount",
            "non_refundable_amount",
            "refund_reason",
            "refund_date",
            "generated_from_rejection",
            "bank_detail_snapshot",
            "payment_summary_snapshot",
            "applicant_snapshot",
            "notes",
            "created_by",
            "approved_by",
            "paid_at",
            "receipt_count",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class ApplicantRefundSummarySerializer(serializers.Serializer):

    payment_summary = serializers.SerializerMethodField()
    refund_breakdown = serializers.SerializerMethodField()
    latest_refund = serializers.SerializerMethodField()

    def get_payment_summary(self, applicant):
        return get_applicant_payment_summary(
            applicant,
        )

    def get_refund_breakdown(self, applicant):
        breakdown = calculate_refund_breakdown(
            applicant,
        )

        return {
            key: str(value)
            for key, value in breakdown.items()
        }

    def get_latest_refund(self, applicant):
        refund = applicant.refunds.order_by(
            "-created_at",
        ).first()

        if not refund:
            return None

        return ApplicantRefundSerializer(
            refund,
        ).data


class GenerateRefundSerializer(serializers.Serializer):

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    def save(self, **kwargs):
        applicant = self.context["applicant"]
        user = self.context.get(
            "user",
        )

        return create_refund_for_rejected_applicant(
            applicant,
            created_by=user if getattr(user, "is_authenticated", False) else None,
            reason=self.validated_data.get(
                "reason",
                "",
            ),
        )


class ApplicantRefundReceiptSerializer(serializers.ModelSerializer):

    applicant_name = serializers.CharField(
        source="applicant.full_name",
        read_only=True,
    )

    application_id = serializers.CharField(
        source="applicant.application_id",
        read_only=True,
    )

    generated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ApplicantRefundReceipt

        fields = (
            "id",
            "applicant",
            "application_id",
            "applicant_name",
            "refund",
            "receipt_number",
            "receipt_type",
            "refund_percentage",
            "refundable_payment_total",
            "refund_amount",
            "non_refundable_amount",
            "refund_reason",
            "refund_bank_snapshot",
            "applicant_snapshot",
            "payment_summary_snapshot",
            "summary_text",
            "notes",
            "generated_by",
            "generated_by_name",
            "generated_at",
            "is_void",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_generated_by_name(self, obj):
        if obj.generated_by:
            return obj.generated_by.get_full_name()

        return None


class GenerateRefundReceiptSerializer(serializers.Serializer):

    refund = serializers.PrimaryKeyRelatedField(
        queryset=ApplicantRefund.objects.all(),
    )

    force_new = serializers.BooleanField(
        required=False,
        default=False,
    )

    def validate_refund(self, refund):
        applicant = self.context.get(
            "applicant",
        )

        if applicant and refund.applicant_id != applicant.id:
            raise serializers.ValidationError(
                "Refund does not belong to this applicant."
            )

        return refund

    def save(self, **kwargs):
        applicant = self.context["applicant"]
        user = self.context.get(
            "user",
        )

        return generate_refund_receipt_for_applicant(
            applicant,
            self.validated_data["refund"],
            generated_by=user if getattr(user, "is_authenticated", False) else None,
            force_new=self.validated_data.get(
                "force_new",
                False,
            ),
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

    assigned_staff = serializers.SerializerMethodField()

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
            "payment_plan_installments",
            "assigned_staff",
            "assigned_staff_name",
            "lawyer",
            "created_at",
        )

        read_only_fields = (
            "id",
            "application_id",
            "created_at",
        )

    def get_assigned_staff_name(self, obj):
        staff = getattr(
            getattr(obj, "slot", None),
            "staff",
            None,
        )

        if staff:
            return staff.user.get_full_name()

        return None

    def get_assigned_staff(self, obj):
        staff = getattr(
            getattr(obj, "slot", None),
            "staff",
            None,
        )

        if staff:
            return str(staff.id)

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

    money_receipts = ApplicantMoneyReceiptSerializer(
        many=True,
        read_only=True,
    )

    refund_bank_detail = ApplicantRefundBankDetailSerializer(
        read_only=True,
    )

    refunds = ApplicantRefundSerializer(
        many=True,
        read_only=True,
    )

    refund_receipts = ApplicantRefundReceiptSerializer(
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

    assigned_staff = serializers.SerializerMethodField()

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
            "payment_plan_installments",
            "visa",
            "visa_name",
            "status",
            "slot",
            "slot_month",
            "assigned_staff",
            "assigned_staff_name",
            "agreement",
            "lawyer",
            "tags",
            "profile",
            "addresses",
            "payments",
            "refund_bank_detail",
            "money_receipts",
            "refunds",
            "refund_receipts",
            "documents",
            "notes",
            "status_history",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_assigned_staff_name(self, obj):
        staff = getattr(
            getattr(obj, "slot", None),
            "staff",
            None,
        )

        if staff:
            return staff.user.get_full_name()

        return None

    def get_assigned_staff(self, obj):
        staff = getattr(
            getattr(obj, "slot", None),
            "staff",
            None,
        )

        if staff:
            return str(staff.id)

        return None
