from rest_framework import serializers
from django.db.models import Count, Sum
from django.utils import timezone

from applicant.models import Applicant
from staff.models import StaffMonthlySlot, StaffPublicProfile
from applicant.models import ApplicantPayment, ApplicantRefund


class PublicApplicantStatusCheckSerializer(serializers.Serializer):
    application_id = serializers.CharField(
        max_length=50,
    )
    email = serializers.EmailField()
    phone = serializers.CharField(
        max_length=30,
    )

    def validate_application_id(self, value):
        return value.strip().upper()

    def validate_phone(self, value):
        return value.strip()


class PublicApplicantStatusHistorySerializer(serializers.Serializer):
    status = serializers.CharField(
        source="new_status.name",
    )
    color = serializers.CharField(
        source="new_status.color",
    )
    changed_at = serializers.DateTimeField(
        source="created_at",
    )


class PublicApplicantPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantPayment
        fields = [
            "id",
            "amount",
            "installment_type",
            "payment_method",
            "receipt_number",
            "payment_date",
        ]


class PublicApplicantRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantRefund
        fields = [
            "id",
            "refund_amount",
            "refund_reason",
            "refund_status",
            "refund_method",
            "created_at",
        ]


class PublicApplicantStatusSerializer(serializers.ModelSerializer):
    status = serializers.CharField(
        source="status.name",
    )
    status_color = serializers.CharField(
        source="status.color",
    )
    visa = serializers.CharField(
        source="visa.name",
    )
    job = serializers.CharField(
        source="job.title",
    )
    country = serializers.CharField(
        source="visa.country.name",
    )
    photo = serializers.SerializerMethodField()
    assigned_staff = serializers.SerializerMethodField()
    status_history = serializers.SerializerMethodField()
    payments = PublicApplicantPaymentSerializer(many=True, read_only=True)
    refunds = PublicApplicantRefundSerializer(many=True, read_only=True)

    class Meta:
        model = Applicant
        fields = [
            "application_id",
            "full_name",
            "photo",
            "visa",
            "job",
            "country",
            "status",
            "status_color",
            "assigned_staff",
            "status_history",
            "payments",
            "refunds",
            "created_at",
            "updated_at",
        ]

    def get_photo(self, obj):
        if not obj.photo:
            return None
        return obj.photo.url if hasattr(obj.photo, 'url') else None

    def get_assigned_staff(self, obj):
        staff = getattr(
            getattr(obj, "slot", None),
            "staff",
            None,
        )

        if not staff:
            return None

        public_profile = getattr(
            staff,
            "public_profile",
            None,
        )

        return {
            "name": staff.user.get_full_name(),
            "designation": getattr(staff.designation, "name", ""),
            "public_slug": public_profile.slug
            if public_profile and public_profile.is_public
            else None,
        }

    def get_status_history(self, obj):
        histories = obj.status_history.select_related(
            "new_status",
        ).order_by(
            "created_at",
        )

        return PublicApplicantStatusHistorySerializer(
            histories,
            many=True,
        ).data


class PublicApplicantResultSerializer(serializers.Serializer):
    application_id = serializers.CharField()
    applicant_name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    visa = serializers.SerializerMethodField()
    job = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    result_date = serializers.DateTimeField()
    passport_number = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    def get_photo(self, obj):
        if not obj.photo:
            return None
        return obj.photo.url if hasattr(obj.photo, 'url') else None

    def get_applicant_name(self, obj):
        return getattr(obj, "full_name", getattr(obj, "applicant_name", ""))

    def get_status(self, obj):
        return obj.status.name if obj.status else ""

    def get_visa(self, obj):
        return obj.visa.name if obj.visa else ""

    def get_job(self, obj):
        return obj.job.title if obj.job else ""

    def get_country(self, obj):
        if hasattr(obj, "country") and obj.country:
            return obj.country.name
        if hasattr(obj, "visa") and obj.visa and obj.visa.country:
            return obj.visa.country.name
        return ""

    def get_passport_number(self, obj):
        p_num = obj.passport_number or ""
        if len(p_num) < 5:
            return "*****"
        return f"{p_num[:3]}***{p_num[-2:]}"

    def get_email(self, obj):
        if hasattr(obj, "profile"):
            email = obj.profile.email if obj.profile else ""
        else:
            email = getattr(obj, "email", "")
            
        if not email or "@" not in email:
            return "*@*"
            
        name_part, domain = email.split("@", 1)
        if len(name_part) <= 3:
            masked_name = f"{name_part[0]}***"
        else:
            masked_name = f"{name_part[0]}***{name_part[-2:]}"
        return f"{masked_name}@{domain}"


class PublicStaffMonthlySlotSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="user.get_full_name", read_only=True)
    designation = serializers.CharField(source="designation.name", read_only=True, allow_null=True)
    office = serializers.CharField(source="office.branch_name", read_only=True, allow_null=True)
    gender = serializers.CharField()
    nationality = serializers.CharField()
    public_slug = serializers.SerializerMethodField()
    staff_slug = serializers.SerializerMethodField()
    total_slot = serializers.SerializerMethodField()
    used_slot = serializers.SerializerMethodField()
    remaining_slot = serializers.SerializerMethodField()

    class Meta:
        from staff.models import Staff
        model = Staff
        fields = [
            "id", "employee_id", "staff_name", "designation", "office",
            "gender", "nationality", "photo", "public_slug", "staff_slug", 
            "total_slot", "used_slot", "remaining_slot"
        ]

    def get_public_slug(self, obj):
        public_profile = getattr(obj, "public_profile", None)
        return public_profile.slug if public_profile and public_profile.is_public else None

    def get_staff_slug(self, obj):
        return self.get_public_slug(obj)

    def _get_current_month_slot(self, obj):
        if hasattr(obj, 'current_month_slots') and obj.current_month_slots:
            return obj.current_month_slots[0]
        return None

    def get_total_slot(self, obj):
        slot = self._get_current_month_slot(obj)
        return slot.total_slot if slot else 0

    def get_used_slot(self, obj):
        slot = self._get_current_month_slot(obj)
        return slot.used_slot_count if slot and hasattr(slot, 'used_slot_count') else 0

    def get_remaining_slot(self, obj):
        return self.get_total_slot(obj) - self.get_used_slot(obj)


class PublicStaffProfileAccessSerializer(serializers.Serializer):
    employee_id = serializers.CharField(
        max_length=50,
    )
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )


class PublicStaffProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    slot_summary = serializers.SerializerMethodField()
    sub_staffs = serializers.SerializerMethodField()

    class Meta:
        model = StaffPublicProfile
        fields = [
            "slug",
            "slot_summary",
            "profile",
            "sub_staffs",
        ]

    def get_slot_summary(self, obj):
        today = timezone.localdate()
        month_start = today.replace(
            day=1,
        )
        staff = obj.staff

        current_month_slot = staff.monthly_slots.filter(
            allocation_month=month_start,
        ).annotate(
            used_slot=Count(
                "applicants",
            ),
        ).first()

        lifetime = staff.monthly_slots.aggregate(
            total_slot=Sum(
                "total_slot",
            ),
            used_slot=Count(
                "applicants",
            ),
        )

        current_total = current_month_slot.total_slot if current_month_slot else 0
        current_used = current_month_slot.used_slot if current_month_slot else 0

        approved_count = Applicant.objects.filter(
            slot__staff=staff,
            status__name__icontains="approved"
        ).count()

        rejected_count = Applicant.objects.filter(
            slot__staff=staff,
            status__name__icontains="rejected"
        ).count()

        processing_count = Applicant.objects.filter(
            slot__staff=staff,
            status__name__icontains="processing"
        ).count()

        return {
            "current_month": month_start,
            "current_month_total_slot": current_total,
            "current_month_used_slot": current_used,
            "current_month_remaining_slot": max(
                current_total - current_used,
                0,
            ),
            "lifetime_total_slot": lifetime["total_slot"] or 0,
            "lifetime_used_slot": lifetime["used_slot"] or 0,
            "approved_visas": approved_count,
            "rejected_visas": rejected_count,
            "processing_visas": processing_count,
        }

    def get_sub_staffs(self, obj):
        sub_staffs = obj.staff.sub_staffs.filter(is_active=True)
        return [
            {
                "id": str(sub.id),
                "name": sub.name,
                "phone": sub.phone,
            }
            for sub in sub_staffs
        ]

    def get_profile(self, obj):
        staff = obj.staff
        fields = obj.public_fields or []

        values = {
            "employee_id": staff.employee_id,
            "full_name": staff.user.get_full_name(),
            "email": staff.user.email,
            "photo": self._file_url(staff.photo),
            "signature": self._file_url(staff.signature),
            "designation": getattr(staff.designation, "name", ""),
            "office": getattr(staff.office, "branch_name", ""),
            "phone": staff.phone,
            "whatsapp": staff.whatsapp,
            "gender": staff.gender,
            "nationality": staff.nationality,
            "joining_date": staff.joining_date,
            "reference_staff": staff.reference_staff.user.get_full_name() if staff.reference_staff else None,
        }

        return {
            field: values[field]
            for field in fields
            if field in values
        }

    def _file_url(self, value):
        if not value:
            return None

        request = self.context.get(
            "request",
        )

        if request:
            return request.build_absolute_uri(
                value.url,
            )

        return value.url


from agency.models import ApplicationRequest

class PublicApplicationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationRequest
        fields = [
            "name",
            "email",
            "phone",
            "message",
            "target_visa",
        ]

from agency.models import ContactUs

class PublicContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'phone', 'subject', 'message']
