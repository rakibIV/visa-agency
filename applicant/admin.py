from django.contrib import admin

from .forms import (
    AgreementTemplateForm,
    ApplicantAddressForm,
    ApplicantCreateForm,
    ApplicantDocumentForm,
    ApplicantNoteForm,
    ApplicantPaymentForm,
    ApplicantProfileForm,
    ApplicantTagForm,
    ApplicantUpdateForm,
    ApplicationStatusForm,
)

from .models import (
    AgreementTemplate,
    Applicant,
    ApplicantAddress,
    ApplicantDocument,
    ApplicantNote,
    ApplicantPayment,
    ApplicantProfile,
    ApplicantStatusHistory,
    ApplicantTag,
    ApplicationStatus,
)


# ==========================================================
# Lookup Admins
# ==========================================================

@admin.register(ApplicationStatus)
class ApplicationStatusAdmin(admin.ModelAdmin):

    form = ApplicationStatusForm

    list_display = [
        "name",
        "display_order",
        "is_default",
        "is_final",
        "is_active",
    ]

    list_editable = [
        "display_order",
        "is_active",
    ]

    list_filter = [
        "is_default",
        "is_final",
        "is_active",
    ]

    search_fields = [
        "name",
        "slug",
    ]

    prepopulated_fields = {
        "slug": (
            "name",
        ),
    }

    ordering = [
        "display_order",
        "name",
    ]


@admin.register(ApplicantTag)
class ApplicantTagAdmin(admin.ModelAdmin):

    form = ApplicantTagForm

    list_display = [
        "name",
        "color",
    ]

    search_fields = [
        "name",
    ]


@admin.register(AgreementTemplate)
class AgreementTemplateAdmin(admin.ModelAdmin):

    form = AgreementTemplateForm

    list_display = [
        "title",
        "visa",
        "version",
        "is_active",
    ]

    list_filter = [
        "visa",
        "is_active",
    ]

    search_fields = [
        "title",
        "body",
    ]

    autocomplete_fields = [
        "visa",
    ]

    ordering = [
        "title",
        "-version",
    ]


# ==========================================================
# Applicant Inlines
# ==========================================================

class ApplicantProfileInline(admin.StackedInline):

    model = ApplicantProfile

    form = ApplicantProfileForm

    extra = 0

    can_delete = False


class ApplicantAddressInline(admin.TabularInline):

    model = ApplicantAddress

    form = ApplicantAddressForm

    extra = 0


class ApplicantPaymentInline(admin.TabularInline):

    model = ApplicantPayment

    form = ApplicantPaymentForm

    extra = 0

    readonly_fields = [
        "payment_number",
        "euro_amount",
    ]


class ApplicantDocumentInline(admin.TabularInline):

    model = ApplicantDocument

    form = ApplicantDocumentForm

    extra = 0

    readonly_fields = [
        "verified",
        "verified_by",
        "verified_at",
    ]


class ApplicantNoteInline(admin.TabularInline):

    model = ApplicantNote

    form = ApplicantNoteForm

    extra = 0


class ApplicantStatusHistoryInline(admin.TabularInline):

    model = ApplicantStatusHistory

    extra = 0

    can_delete = False

    readonly_fields = [
        "old_status",
        "new_status",
        "changed_by",
        "remarks",
        "created_at",
    ]


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):

    list_display = [
        "application_id",
        "full_name",
        "passport_number",
        "visa",
        "status",
        "slot",
        "created_at",
    ]

    list_filter = [
        "status",
        "visa",

        "slot",
        "created_at",
    ]

    search_fields = [
        "application_id",
        "full_name",
        "passport_number",
        "nid_number",
        "profile__phone",
        "profile__email",
    ]

    ordering = [
        "-created_at",
    ]

    readonly_fields = [
        "application_id",
        "created_at",
        "updated_at",
    ]

    autocomplete_fields = [
        "visa",
        "status",
        "slot",
        "agreement",
        "tags",
        "created_by",
        "updated_by",
    ]

    inlines = [
        ApplicantProfileInline,
        ApplicantAddressInline,
        ApplicantPaymentInline,
        ApplicantDocumentInline,
        ApplicantNoteInline,
        ApplicantStatusHistoryInline,
    ]

    fieldsets = (
        (
            "Application Information",
            {
                "fields": (
                    "application_id",
                    "status",
                    "visa",
                    "agreement",
                    "tags",
                )
            },
        ),
        (
            "Applicant Information",
            {
                "fields": (
                    "full_name",
                    "photo",
                    "passport_number",
                    "passport_issue_date",
                    "passport_expiry_date",
                    "nid_number",
                    "date_of_birth",
                    "place_of_birth",
                    "current_country",
                )
            },
        ),
        (
            "Staff Assignment",
            {
                "fields": (
                    "slot",
                )
            },
        ),
        (
            "Audit",
            {
                "fields": (
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "fields": (
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
                    "status",
                "slot",
                "agreement",
                "tags",
                "created_by",
                    "updated_by",
                )
            },
        ),
    )

    def get_queryset(self, request):

        return (
            super()
            .get_queryset(request)
            .select_related(
                "visa",
                "status",
                "slot",
                "slot__staff",
                "assigned_staff",
                "agreement",
            )
            .prefetch_related(
                "tags",
            )
        )

    def get_form(
        self,
        request,
        obj=None,
        **kwargs,
    ):

        if obj is None:
            kwargs["form"] = ApplicantCreateForm
        else:
            kwargs["form"] = ApplicantUpdateForm

        return super().get_form(
            request,
            obj,
            **kwargs,
        )

    def get_fieldsets(
        self,
        request,
        obj=None,
    ):

        if obj is None:
            return self.add_fieldsets

        return super().get_fieldsets(
            request,
            obj,
        )
    

# ==========================================================
# Applicant Address
# ==========================================================

@admin.register(ApplicantAddress)
class ApplicantAddressAdmin(admin.ModelAdmin):

    form = ApplicantAddressForm

    list_display = [
        "applicant",
        "address_type",
        "country",
    ]

    list_filter = [
        "address_type",
        "country",
    ]

    search_fields = [
        "applicant__application_id",
        "applicant__full_name",
        "district",
        "police_station",
        "post_office",
        "village",
    ]

    autocomplete_fields = [
        "applicant",
        "country",
    ]

    ordering = [
        "applicant",
        "address_type",
    ]


# ==========================================================
# Applicant Payment
# ==========================================================

@admin.register(ApplicantPayment)
class ApplicantPaymentAdmin(admin.ModelAdmin):

    form = ApplicantPaymentForm

    list_display = [
        "applicant",
        "payment_number",
        "payment_date",
        "payment_method",
        "currency",
        "amount",
        "euro_amount",
        "received_by",
    ]

    list_filter = [
        "payment_method",
        "currency",
        "payment_date",
    ]

    search_fields = [
        "applicant__application_id",
        "applicant__full_name",
    ]

    autocomplete_fields = [
        "applicant",
        "received_by",
    ]

    readonly_fields = [
        "payment_number",
        "euro_amount",
    ]

    ordering = [
        "-payment_date",
        "-payment_number",
    ]


# ==========================================================
# Applicant Document
# ==========================================================

@admin.register(ApplicantDocument)
class ApplicantDocumentAdmin(admin.ModelAdmin):

    form = ApplicantDocumentForm

    list_display = [
        "applicant",
        "document_type",
        "verified",
        "verified_by",
        "verified_at",
    ]

    list_filter = [
        "document_type",
        "verified",
    ]

    search_fields = [
        "applicant__application_id",
        "applicant__full_name",
    ]

    autocomplete_fields = [
        "applicant",
        "verified_by",
    ]

    readonly_fields = [
        "verified",
        "verified_by",
        "verified_at",
    ]

    ordering = [
        "document_type",
    ]


# ==========================================================
# Applicant Notes
# ==========================================================

@admin.register(ApplicantNote)
class ApplicantNoteAdmin(admin.ModelAdmin):

    form = ApplicantNoteForm

    list_display = [
        "applicant",
        "staff",
        "created_at",
    ]

    list_filter = [
        "created_at",
    ]

    search_fields = [
        "applicant__application_id",
        "applicant__full_name",
        "note",
    ]

    autocomplete_fields = [
        "applicant",
        "staff",
    ]

    ordering = [
        "-created_at",
    ]


# ==========================================================
# Status History
# ==========================================================

@admin.register(ApplicantStatusHistory)
class ApplicantStatusHistoryAdmin(admin.ModelAdmin):

    list_display = [
        "applicant",
        "old_status",
        "new_status",
        "changed_by",
        "created_at",
    ]

    list_filter = [
        "new_status",
        "created_at",
    ]

    search_fields = [
        "applicant__application_id",
        "applicant__full_name",
        "remarks",
    ]

    autocomplete_fields = [
        "applicant",
        "old_status",
        "new_status",
        "changed_by",
    ]

    readonly_fields = [
        "applicant",
        "old_status",
        "new_status",
        "changed_by",
        "remarks",
        "created_at",
        "updated_at",
    ]

    ordering = [
        "-created_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
