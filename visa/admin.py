
# Register your models here.
from django.contrib import admin

from .models import (
    VisaCategory,
    Visa,
    VisaRequirement,
    VisaStep,
    VisaFAQ,
    VisaSEO,
    VisaJob,
    JobFacility,
)


@admin.register(VisaCategory)
class VisaCategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "is_featured",
        "is_active",
        "display_order",
    ]

    list_filter = [
        "is_featured",
        "is_active",
    ]

    search_fields = [
        "name",
    ]

    prepopulated_fields = {
        "slug": [
            "name",
        ]
    }

    ordering = [
        "display_order",
        "name",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]


@admin.register(Visa)
class VisaAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "country",
        "category",
        "is_featured",
        "is_active",
        "display_order",
    ]

    list_filter = [
        "country",
        "category",
        "is_featured",
        "is_active",
    ]

    search_fields = [
        "name",
        "country__name",
        "category__name",
    ]

    autocomplete_fields = [
        "country",
        "category",
        "services",
    ]

    filter_horizontal = [
        "services",
    ]

    ordering = [
        "display_order",
        "name",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]


@admin.register(VisaRequirement)
class VisaRequirementAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "visa",
        "requirement_type",
        "is_required",
        "is_active",
        "display_order",
    ]

    list_filter = [
        "requirement_type",
        "is_required",
        "is_active",
    ]

    search_fields = [
        "title",
        "visa__name",
    ]

    autocomplete_fields = [
        "visa",
    ]

    ordering = [
        "display_order",
        "title",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]


@admin.register(VisaStep)
class VisaStepAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "visa",
        "display_order",
        "is_active",
    ]

    list_filter = [
        "is_active",
    ]

    search_fields = [
        "title",
        "visa__name",
    ]

    autocomplete_fields = [
        "visa",
    ]

    ordering = [
        "display_order",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]


@admin.register(VisaFAQ)
class VisaFAQAdmin(admin.ModelAdmin):
    list_display = [
        "question",
        "visa",
        "display_order",
        "is_active",
    ]

    list_filter = [
        "is_active",
    ]

    search_fields = [
        "question",
        "visa__name",
    ]

    autocomplete_fields = [
        "visa",
    ]

    ordering = [
        "display_order",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]


@admin.register(VisaSEO)
class VisaSEOAdmin(admin.ModelAdmin):
    list_display = [
        "visa",
        "meta_title",
    ]

    search_fields = [
        "visa__name",
        "meta_title",
    ]

    autocomplete_fields = [
        "visa",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]

class JobFacilityInline(admin.TabularInline):
    model = JobFacility
    extra = 1

inlines = [
    JobFacilityInline,
]


@admin.register(VisaJob)
class VisaJobAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "visa",
        "minimum_salary",
        "maximum_salary",
        "vacancies",
        "is_active",
    ]

    list_filter = [
        "visa",
        "is_active",
        "is_featured",
    ]

    search_fields = [
        "title",
        "visa__name",
    ]

    list_editable = [
        "is_active",
    ]



    inlines = [
        JobFacilityInline,
    ]


@admin.register(JobFacility)
class JobFacilityAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "job",
        "is_active",
    ]

    list_filter = [
        "is_active",
    ]

    search_fields = [
        "title",
        "job__title",
    ]