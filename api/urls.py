from django.urls import include, path
# 1. Use the correct package import for nested routing
from rest_framework_nested import routers 
from country.views import (
    CountryViewSet, 
    CountryRequirementViewSet, 
    CountryGalleryViewSet, 
    CountryFAQViewSet, 
    CountrySEOViewSet
)

# Base Router
router = routers.DefaultRouter()
router.register("countries", CountryViewSet, basename="country")

# 2. Child Router hooked to the parent
country_router = routers.NestedDefaultRouter(
    router,
    "countries",
    lookup="country", # This creates the variable name 'country_pk' for your views
)

country_router.register(
    "requirements",
    CountryRequirementViewSet,
    basename="country-requirements",
)

country_router.register(
    "faqs",
    CountryFAQViewSet,
    basename="country-faqs",
)

country_router.register(
    "gallery",
    CountryGalleryViewSet,
    basename="country-gallery",
)

# 3. Correctly combine both parent and child URLs into urlpatterns
urlpatterns = [
    path("", include(router.urls)),
    path("", include(country_router.urls)),
]