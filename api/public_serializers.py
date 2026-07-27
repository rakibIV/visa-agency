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
            "currency",
            "euro_amount",
            "exchange_rate",
            "installment_type",
            "payment_method",
            "receipt_number",
            "payment_date",
            "countdown_days",
            "important_note",
            "note",
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
            "receipt_number",
            "created_at",
        ]


class PublicApplicantStatusSerializer(serializers.ModelSerializer):
    status = serializers.CharField(
        source="status.name",
        default="",
    )
    status_color = serializers.CharField(
        source="status.color",
        default="",
    )
    visa = serializers.CharField(
        source="visa.name",
        default="",
    )
    job = serializers.SerializerMethodField()
    secondary_job = serializers.SerializerMethodField()
    country = serializers.CharField(
        source="visa.country.name",
        default="",
    )
    photo = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    father_name = serializers.SerializerMethodField()
    mother_name = serializers.SerializerMethodField()
    nationality = serializers.SerializerMethodField()
    status_history = serializers.SerializerMethodField()
    lawyer_name = serializers.SerializerMethodField()
    lawyer_address = serializers.SerializerMethodField()
    countdown_info = serializers.SerializerMethodField()
    payments = PublicApplicantPaymentSerializer(many=True, read_only=True)
    refunds = PublicApplicantRefundSerializer(many=True, read_only=True)

    class Meta:
        model = Applicant
        fields = [
            "application_id",
            "full_name",
            "passport_number",
            "date_of_birth",
            "nid_number",
            "place_of_birth",
            "current_country",
            "phone",
            "email",
            "father_name",
            "mother_name",
            "nationality",
            "photo",
            "visa",
            "job",
            "secondary_job",
            "country",
            "status",
            "status_color",
            "lawyer_name",
            "lawyer_address",
            "countdown_info",
            "status_history",
            "payments",
            "refunds",
            "created_at",
            "updated_at",
        ]

    def get_countdown_info(self, obj):
        payments = obj.payments.all()
        target_payment = None
        
        for p in payments:
            if p.countdown_days and p.countdown_days > 0:
                target_payment = p
                break
        
        if not target_payment:
            if len(payments) >= 2 and payments[1].countdown_days:
                target_payment = payments[1]

        if not target_payment or not target_payment.countdown_days:
            return None

        today = timezone.localdate()
        payment_date = target_payment.payment_date
        days_elapsed = max(0, (today - payment_date).days)
        target_days = target_payment.countdown_days
        is_overdue = days_elapsed > target_days

        return {
            "target_days": target_days,
            "days_elapsed": days_elapsed,
            "is_overdue": is_overdue,
            "payment_date": payment_date,
            "installment_type": target_payment.installment_type,
        }

    def get_lawyer_name(self, obj):
        if getattr(obj, "lawyer", None):
            return obj.lawyer.name
        return ""

    def get_lawyer_address(self, obj):
        if getattr(obj, "lawyer", None):
            return obj.lawyer.address
        return ""

    def get_job(self, obj):
        if not getattr(obj, "job", None):
            return None
        return getattr(obj.job, "title", None) or str(obj.job)

    def get_secondary_job(self, obj):
        if not getattr(obj, "secondary_job", None):
            return None
        return getattr(obj.secondary_job, "title", None) or str(obj.secondary_job)

    def get_phone(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.phone if profile and profile.phone else None

    def get_email(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.email if profile and profile.email else None

    def get_father_name(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.father_name if profile and profile.father_name else None

    def get_mother_name(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.mother_name if profile and profile.mother_name else None

    def get_nationality(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.nationality if profile and profile.nationality else None

    def get_photo(self, obj):
        if not obj.photo:
            return None
        return obj.photo.url if hasattr(obj.photo, 'url') else None

    def get_status_history(self, obj):
        histories = list(
            obj.status_history.select_related(
                "new_status",
            ).order_by("created_at")
        )

        seen_status_ids = set()
        unique_histories = []

        for h in histories:
            if not h.new_status or h.new_status_id in seen_status_ids:
                continue
            seen_status_ids.add(h.new_status_id)
            unique_histories.append(h)

        return PublicApplicantStatusHistorySerializer(
            unique_histories,
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
    is_approved = serializers.SerializerMethodField()
    is_rejected = serializers.SerializerMethodField()

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

    def get_is_approved(self, obj):
        if not getattr(obj, "status", None):
            return False
        st_name = (obj.status.name or "").lower()
        st_slug = (getattr(obj.status, "slug", "") or "").lower()
        if "approve" in st_name or "approve" in st_slug:
            return True
        from applicant.selectors import get_approved_status_ids
        return obj.status.id in get_approved_status_ids()

    def get_is_rejected(self, obj):
        if not getattr(obj, "status", None):
            return False
        st_name = (obj.status.name or "").lower()
        st_slug = (getattr(obj.status, "slug", "") or "").lower()
        if any(k in st_name or k in st_slug for k in ["reject", "refus", "cancel"]):
            return True
        from applicant.selectors import get_rejected_status_ids
        return obj.status.id in get_rejected_status_ids()

    def get_passport_number(self, obj):
        p_num = obj.passport_number or ""
        if len(p_num) < 6:
            return f"{p_num[:3]}***" if len(p_num) >= 3 else "***"
        return f"{p_num[:3]}***{p_num[-3:]}"

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

        from applicant.selectors import get_approved_status_ids, get_rejected_status_ids

        approved_ids = get_approved_status_ids()
        rejected_ids = get_rejected_status_ids()

        real_approved = Applicant.objects.filter(
            slot__staff=staff,
            is_deleted=False,
            status_id__in=approved_ids
        ).count()
        approved_count = real_approved + (getattr(staff, "fake_approved_count", 0) or 0)

        real_rejected = Applicant.objects.filter(
            slot__staff=staff,
            is_deleted=False,
            status_id__in=rejected_ids
        ).count()
        rejected_count = real_rejected + (getattr(staff, "fake_rejected_count", 0) or 0)

        total_real = Applicant.objects.filter(
            slot__staff=staff,
            is_deleted=False
        ).count()
        processing_count = max(0, total_real - real_approved - real_rejected)

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
            "joining_date": str(staff.joining_date) if staff.joining_date else None,
            "father_name": staff.father_name,
            "passport_number": staff.passport_number,
            "date_of_birth": str(staff.date_of_birth) if staff.date_of_birth else None,
            "reference_staff": staff.reference_staff.user.get_full_name() if staff.reference_staff else None,
            "monthly_rank": staff.monthly_rank,
            "yearly_rank": staff.yearly_rank,
        }

        # Include requested or new public fields
        extra_always_included = {"father_name", "passport_number", "date_of_birth", "joining_date", "gender", "nationality", "monthly_rank", "yearly_rank"}
        return {
            k: v
            for k, v in values.items()
            if not fields or k in fields or k in extra_always_included
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
