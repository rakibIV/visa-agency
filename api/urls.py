from django.urls import include, path
# 1. Use the correct package import for nested routing
from rest_framework_nested import routers 
from country.views import (
    CountryViewSet, 
    CountryRequirementViewSet, 
    CountryGalleryViewSet, 
    CountryFAQViewSet
)

from agency.views import (
    CompanyInformationViewSet,
    OfficeViewSet,
    SocialLinkViewSet,
    AgencyServiceViewSet,
    EmailTemplateViewSet,
)

# Base Router
router = routers.DefaultRouter()
router.register("countries", CountryViewSet, basename="country")
router.register("company", CompanyInformationViewSet, basename="company")

# 2. Child Router hooked to the parent
country_router = routers.NestedDefaultRouter(
    router,
    "countries",
    lookup="country", # This creates the variable name 'country_pk' for your views
)


company_router = routers.NestedDefaultRouter(
    router,
    "company",
    lookup="company",
)

country_router.register('requirements', CountryRequirementViewSet, basename='country-requirement')
country_router.register('faqs', CountryFAQViewSet, basename='country-faq')
country_router.register('gallery', CountryGalleryViewSet, basename='country-gallery')

router.register("company", CompanyInformationViewSet, basename="company")
router.register("offices", OfficeViewSet, basename="office")
router.register("social-links", SocialLinkViewSet, basename="social-link")
router.register("agency-services", AgencyServiceViewSet, basename="agency-service")
router.register("email-templates", EmailTemplateViewSet, basename="email-template")

# 3. Correctly combine both parent and child URLs into urlpatterns
urlpatterns = [
    path("", include(router.urls)),
    path("", include(country_router.urls)),
]