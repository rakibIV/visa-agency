from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

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
from visa.views import (
    VisaCategoryViewSet,
    VisaViewSet,
    VisaRequirementViewSet,
    VisaStepViewSet,
    VisaFAQViewSet,
    VisaSEOViewSet,
    VisaJobViewSet,
    JobFacilityViewSet,
)

from staff.views import (
    DesignationViewSet,
    StaffViewSet,
    StaffMonthlySlotViewSet,
    StaffDocumentViewSet,
    StaffEmergencyContactViewSet,
)

# ==========================================
# 1. BASE ROUTER (Top-Level Endpoints)
# ==========================================
router = DefaultRouter()
router.register("countries", CountryViewSet, basename="country")
router.register("companies", CompanyInformationViewSet, basename="company")
router.register("visa-categories", VisaCategoryViewSet, basename="visa-category")
router.register("visas", VisaViewSet, basename="visa")
router.register("offices", OfficeViewSet, basename="office")
router.register("social-links", SocialLinkViewSet, basename="social-link")
router.register("agency-services", AgencyServiceViewSet, basename="agency-service")
router.register("email-templates", EmailTemplateViewSet, basename="email-template")

# Staff Core Endpoints
router.register("designations", DesignationViewSet, basename="designation")
router.register("staffs", StaffViewSet, basename="staff")

# Staff Child Routing
staff_router = NestedDefaultRouter(router, "staffs", lookup="staff")
staff_router.register("monthly-slots", StaffMonthlySlotViewSet, basename="staff-monthly-slot")
staff_router.register("documents", StaffDocumentViewSet, basename="staff-document")
staff_router.register("emergency-contacts", StaffEmergencyContactViewSet, basename="staff-emergency-contact")

# ==========================================
# 2. CHILD ROUTERS (Level 1 Nesting)
# ==========================================
country_router = NestedDefaultRouter(router, "countries", lookup="country")
country_router.register('requirements', CountryRequirementViewSet, basename='country-requirement')
country_router.register('faqs', CountryFAQViewSet, basename='country-faq')
country_router.register('gallery', CountryGalleryViewSet, basename='country-gallery')


visa_router = NestedDefaultRouter(router, "visas", lookup="visa")
visa_router.register('requirements', VisaRequirementViewSet, basename='visa-requirement')
visa_router.register("jobs", VisaJobViewSet, basename="visa-job")
visa_router.register('steps', VisaStepViewSet, basename='visa-step')
visa_router.register('faqs', VisaFAQViewSet, basename='visa-faq')
visa_router.register('seo', VisaSEOViewSet, basename='visa-seo')

# ==========================================
# 3. GRANDCHILD ROUTERS (Level 2 Nesting)
# ==========================================
# This links underneath the "jobs" registration inside the visa_router tree
job_router = NestedDefaultRouter(visa_router, "jobs", lookup="job")
job_router.register("facilities", JobFacilityViewSet, basename="job-facility")

# ==========================================
# 4. URLPATTERNS REGISTRATION
# ==========================================
urlpatterns = [
    path("", include(router.urls)),
    path("", include(country_router.urls)),
    path("", include(visa_router.urls)),
    path("", include(job_router.urls)),
    path("", include(staff_router.urls)),
] 