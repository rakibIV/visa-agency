from django.contrib import admin

from .models import (
    CompanyInformation,
    Office,
    AgencyService,
    SocialLink,
    EmailTemplate,
)


@admin.register(CompanyInformation)
class CompanyInformationAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "phone",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "company_name",
        "phone",
        "address",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = (
        "branch_name",
        "phone",
        "email",
        "is_head_office",
        "is_active",
        "display_order",
    )

    list_filter = (
        "is_head_office",
        "is_active",
    )

    search_fields = (
        "branch_name",
        "phone",
        "email",
    )

    ordering = (
        "display_order",
        "branch_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(AgencyService)
class AgencyServiceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_featured",
        "is_active",
        "display_order",
    )

    list_filter = (
        "is_featured",
        "is_active",
    )

    search_fields = (
        "title",
    )

    ordering = (
        "display_order",
        "title",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = (
        "platform",
        "url",
        "is_active",
        "display_order",
    )

    list_filter = (
        "platform",
        "is_active",
    )

    search_fields = (
        "platform",
        "url",
    )

    ordering = (
        "display_order",
        "platform",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "subject",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "subject",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )