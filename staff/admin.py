from django.contrib import admin

from .forms import (
    StaffCreationForm,
    StaffChangeForm,
)
from .models import (
    Designation,
    Staff,
    StaffMonthlySlot,
    StaffDocument,
    StaffEmergencyContact,
)
from .services import (
    create_staff,
    update_staff,
)
from .utils import (
    get_staff_data,
)


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "display_order",
        "is_active",
    ]

    list_filter = [
        "is_active",
    ]

    search_fields = [
        "name",
    ]

    ordering = [
        "display_order",
        "name",
    ]


class StaffMonthlySlotInline(admin.TabularInline):

    model = StaffMonthlySlot

    extra = 0


class StaffDocumentInline(admin.TabularInline):

    model = StaffDocument

    extra = 0


class StaffEmergencyContactInline(admin.TabularInline):

    model = StaffEmergencyContact

    extra = 0


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):

    list_display = [
        "employee_id",
        "full_name",
        "designation",
        "office",
        "phone",
        "is_active",
    ]

    list_filter = [
        "designation",
        "office",
        "is_active",
    ]

    search_fields = [
        "employee_id",
        "user__first_name",
        "user__last_name",
        "phone",
    ]

    autocomplete_fields = [
        "designation",
        "office",
        "reference_staff",
    ]

    readonly_fields = [
        "employee_id",
    ]

    inlines = [
        StaffMonthlySlotInline,
        StaffDocumentInline,
        StaffEmergencyContactInline,
    ]

    fieldsets = (
        (
            "Account Information",
            {
                "fields": (
                    "employee_id",
                    "photo",
                    "signature",
                ),
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "phone",
                    "whatsapp",
                    "gender",
                    "date_of_birth",
                    "nationality",
                    "father_name",
                    "mother_name",
                ),
            },
        ),
        (
            "Identity",
            {
                "fields": (
                    "nid_number",
                    "passport_number",
                ),
            },
        ),
        (
            "Employment",
            {
                "fields": (
                    "designation",
                    "office",
                    "joining_date",
                    "reference_staff",
                    "is_active",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "password",
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
                    "photo",
                    "signature",
                    "is_active",
                ),
            },
        ),
    )

    def get_form(
        self,
        request,
        obj=None,
        **kwargs,
    ):
        kwargs["form"] = (
            StaffCreationForm
            if obj is None
            else StaffChangeForm
        )

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

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):
        staff_data = get_staff_data(obj)

        if change:

            update_staff(
                staff=obj,
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
                new_password=form.cleaned_data.get(
                    "new_password",
                ),
                staff_data=staff_data,
            )

            return

        create_staff(
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
            staff_data=staff_data,
        )

    @admin.display(
        description="Name",
        ordering="user__first_name",
    )
    def full_name(
        self,
        obj,
    ):
        return obj.user.get_full_name()


@admin.register(StaffMonthlySlot)
class StaffMonthlySlotAdmin(admin.ModelAdmin):

    list_display = [
        "staff",
        "allocation_month",
        "total_slot",
    ]

    list_filter = [
        "allocation_month",
    ]

    search_fields = [
        "staff__employee_id",
        "staff__user__first_name",
        "staff__user__last_name",
    ]

    autocomplete_fields = [
        "staff",
    ]


@admin.register(StaffDocument)
class StaffDocumentAdmin(admin.ModelAdmin):

    list_display = [
        "staff",
        "title",
        "display_order",
        "is_active",
    ]

    list_filter = [
        "is_active",
    ]

    autocomplete_fields = [
        "staff",
    ]


@admin.register(StaffEmergencyContact)
class StaffEmergencyContactAdmin(admin.ModelAdmin):

    list_display = [
        "staff",
        "name",
        "relationship",
        "phone",
    ]

    autocomplete_fields = [
        "staff",
    ]
