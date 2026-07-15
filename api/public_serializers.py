from rest_framework import serializers
from django.db.models import Count, Sum
from django.utils import timezone

from applicant.models import Applicant
from staff.models import StaffMonthlySlot, StaffPublicProfile


class PublicApplicantStatusCheckSerializer(serializers.Serializer):
    application_id = serializers.CharField(
        max_length=8,
    )
    email = serializers.EmailField()
    phone = serializers.CharField(
        max_length=30,
    )

    def validate_application_id(self, value):
        value = value.strip().upper()

        if len(value) != 8 or not value.startswith("ARG"):
            raise serializers.ValidationError(
                "Enter a valid application ID."
            )

        return value

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
    assigned_staff = serializers.SerializerMethodField()
    status_history = serializers.SerializerMethodField()

    class Meta:
        model = Applicant
        fields = [
            "application_id",
            "full_name",
            "visa",
            "job",
            "country",
            "status",
            "status_color",
            "assigned_staff",
            "status_history",
            "created_at",
            "updated_at",
        ]

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


class PublicApplicantResultSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()

    status = serializers.CharField(
        source="status.name",
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
    result_date = serializers.DateTimeField()

    class Meta:
        model = Applicant
        fields = [
            "application_id",
            "applicant_name",
            "visa",
            "job",
            "country",
            "status",
            "result_date",
        ]

    def get_applicant_name(self, obj):
        name = obj.full_name or ""
        parts = name.split()

        if not parts:
            return ""

        first_name = parts[0]

        if len(first_name) <= 2:
            return f"{first_name[0]}***"

        return f"{first_name[:2]}***"


class PublicStaffMonthlySlotSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(
        source="staff.user.get_full_name",
    )
    employee_id = serializers.CharField(
        source="staff.employee_id",
    )
    designation = serializers.CharField(
        source="staff.designation.name",
    )
    office = serializers.CharField(
        source="staff.office.branch_name",
    )
    photo = serializers.ImageField(
        source="staff.photo",
    )
    public_slug = serializers.SerializerMethodField()
    used_slot = serializers.IntegerField()
    remaining_slot = serializers.IntegerField()

    class Meta:
        model = StaffMonthlySlot
        fields = [
            "id",
            "allocation_month",
            "employee_id",
            "staff_name",
            "designation",
            "office",
            "photo",
            "public_slug",
            "total_slot",
            "used_slot",
            "remaining_slot",
        ]

    def get_public_slug(self, obj):
        public_profile = getattr(
            obj.staff,
            "public_profile",
            None,
        )

        if public_profile and public_profile.is_public:
            return public_profile.slug

        return None


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
