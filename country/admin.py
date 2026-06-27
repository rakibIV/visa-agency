from django.contrib import admin

from .models import (
    Country,
    CountryRequirement,
    CountryFAQ,
    CountryGallery,
    CountrySEO,
)

class CountryRequirementInline(admin.TabularInline):
    model = CountryRequirement
    extra = 1


class CountryFAQInline(admin.TabularInline):
    model = CountryFAQ
    extra = 1


class CountryGalleryInline(admin.TabularInline):
    model = CountryGallery
    extra = 1


class CountrySEOInline(admin.StackedInline):
    model = CountrySEO
    extra = 0
    max_num = 1


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "nationality",
        "is_featured",
        "is_active",
        "display_order",
        "created_at",
    )

    list_filter = (
        "is_active",
        "is_featured",
    )

    search_fields = (
        "name",
        "code",
        "nationality",
    )

    ordering = (
        "display_order",
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    list_editable = (
        "display_order",
        "is_featured",
        "is_active",
    )

    inlines = [
        CountryRequirementInline,
        CountryFAQInline,
        CountryGalleryInline,
        CountrySEOInline,
    ]



@admin.register(CountryRequirement)
class CountryRequirementAdmin(admin.ModelAdmin):
    list_display = (
        "country",
        "requirement_type",
        "title",
        "is_required",
        "is_active",
        "display_order",
    )

    list_filter = (
        "country",
        "requirement_type",
        "is_required",
        "is_active",
    )

    search_fields = (
        "title",
        "country__name",
    )

    ordering = (
        "country",
        "display_order",
    )



@admin.register(CountryFAQ)
class CountryFAQAdmin(admin.ModelAdmin):
    list_display = (
        "country",
        "question",
        "display_order",
        "is_active",
    )

    list_filter = (
        "country",
        "is_active",
    )

    search_fields = (
        "question",
        "country__name",
    )

    ordering = (
        "country",
        "display_order",
    )



@admin.register(CountryGallery)
class CountryGalleryAdmin(admin.ModelAdmin):
    list_display = (
        "country",
        "caption",
        "display_order",
        "is_active",
    )

    list_filter = (
        "country",
        "is_active",
    )

    search_fields = (
        "country__name",
        "caption",
    )

    ordering = (
        "country",
        "display_order",
    )


@admin.register(CountrySEO)
class CountrySEOAdmin(admin.ModelAdmin):
    list_display = (
        "country",
        "meta_title",
    )

    search_fields = (
        "country__name",
        "meta_title",
    )