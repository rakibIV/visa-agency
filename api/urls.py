from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from api.swagger import apply_schema_overrides

from api.public_views import (
    PublicApplicantStatusCheckAPIView,
    PublicCurrentMonthApplicantResultListAPIView,
    PublicCurrentMonthStaffSlotListAPIView,
    PublicStaffProfileAccessAPIView,
)

from api.views import (
    UserProfileAPIView,
    UserPasswordUpdateAPIView,
)

# Consolidated Imports by App
from agency.views import (
    AgencyServiceViewSet,
    CompanyInformationViewSet,
    ContactUsViewSet,
    EmailTemplateViewSet,
    LawyerViewSet,
    NoticeViewSet,
    OfficeViewSet,
    ReviewViewSet,
    SocialLinkViewSet,
)
from applicant.views import (
    AgreementTemplateClauseViewSet,
    AgreementTemplateViewSet,
    ApplicantAddressViewSet,
    ApplicantDocumentViewSet,
    ApplicantMoneyReceiptViewSet,
    ApplicantNoteViewSet,
    ApplicantPaymentViewSet,
    ApplicantRefundBankDetailViewSet,
    ApplicantRefundReceiptViewSet,
    ApplicantRefundViewSet,
    ApplicantStatusHistoryViewSet,
    ApplicantTagViewSet,
    ApplicantViewSet,
    ApplicationStatusViewSet,
)
from country.views import (
    CountryFAQViewSet,
    CountryGalleryViewSet,
    CountryRequirementViewSet,
    CountrySEOViewSet,
    CountryViewSet,
)
from staff.views import (
    DesignationViewSet,
    StaffDocumentViewSet,
    StaffEmergencyContactViewSet,
    StaffMonthlySlotViewSet,
    StaffViewSet,
    SubStaffMonthlySlotViewSet,
    SubStaffViewSet,
)
from visa.views import (
    JobFacilityViewSet,
    VisaCategoryViewSet,
    VisaFAQViewSet,
    VisaJobViewSet,
    VisaRequirementViewSet,
    VisaSEOViewSet,
    VisaStepViewSet,
    VisaViewSet,
)

# ==========================================
# 1. BASE ROUTER (Top-Level Endpoints)
# ==========================================
router = DefaultRouter()

# Country & Agency Core
router.register("countries", CountryViewSet, basename="country")
router.register("companies", CompanyInformationViewSet, basename="company")
router.register("branches", OfficeViewSet, basename="office")
router.register("social-links", SocialLinkViewSet, basename="social-link")
router.register("agency-services", AgencyServiceViewSet, basename="agency-service")
router.register("email-templates", EmailTemplateViewSet, basename="email-template")
router.register("lawyers", LawyerViewSet, basename="lawyer")
router.register("notices", NoticeViewSet, basename="notice")
router.register("reviews", ReviewViewSet, basename="review")
router.register("contact-us", ContactUsViewSet, basename="contact-us")

# Visa Core
router.register("visa-categories", VisaCategoryViewSet, basename="visa-category")
router.register("visas", VisaViewSet, basename="visa")

# Staff Core 
router.register("designations", DesignationViewSet, basename="designation")
router.register("staffs", StaffViewSet, basename="staff")

# Applicant Core
router.register("application-statuses", ApplicationStatusViewSet, basename="application-status")
router.register("applicant-tags", ApplicantTagViewSet, basename="applicant-tag")
router.register("agreement-templates", AgreementTemplateViewSet, basename="agreement-template")
router.register("applicants", ApplicantViewSet, basename="applicant")


# ==========================================
# 2. CHILD ROUTERS (Level 1 Nesting)
# ==========================================

# Country Nesting
country_router = NestedDefaultRouter(router, "countries", lookup="country")
country_router.register("requirements", CountryRequirementViewSet, basename="country-requirement")
country_router.register("faqs", CountryFAQViewSet, basename="country-faq")
country_router.register("gallery", CountryGalleryViewSet, basename="country-gallery")
country_router.register("seo", CountrySEOViewSet, basename="country-seo")

# Visa Nesting
visa_router = NestedDefaultRouter(router, "visas", lookup="visa")
visa_router.register("requirements", VisaRequirementViewSet, basename="visa-requirement")
visa_router.register("jobs", VisaJobViewSet, basename="visa-job")
visa_router.register("steps", VisaStepViewSet, basename="visa-step")
visa_router.register("faqs", VisaFAQViewSet, basename="visa-faq")
visa_router.register("seo", VisaSEOViewSet, basename="visa-seo")

# Staff Nesting
staff_router = NestedDefaultRouter(router, "staffs", lookup="staff")
staff_router.register("monthly-slots", StaffMonthlySlotViewSet, basename="staff-monthly-slot")
staff_router.register("sub-staffs", SubStaffViewSet, basename="staff-sub-staff")
staff_router.register("documents", StaffDocumentViewSet, basename="staff-document")
staff_router.register("emergency-contacts", StaffEmergencyContactViewSet, basename="staff-emergency-contact")

sub_staff_router = NestedDefaultRouter(staff_router, "sub-staffs", lookup="sub_staff")
sub_staff_router.register("monthly-slots", SubStaffMonthlySlotViewSet, basename="sub-staff-monthly-slot")

# Applicant Nesting
applicant_router = NestedDefaultRouter(router, "applicants", lookup="applicant")
applicant_router.register("addresses", ApplicantAddressViewSet, basename="applicant-address")
applicant_router.register("payments", ApplicantPaymentViewSet, basename="applicant-payment")
applicant_router.register("money-receipts", ApplicantMoneyReceiptViewSet, basename="applicant-money-receipt")
applicant_router.register("refund-bank-detail", ApplicantRefundBankDetailViewSet, basename="applicant-refund-bank-detail")
applicant_router.register("refunds", ApplicantRefundViewSet, basename="applicant-refund")
applicant_router.register("refund-receipts", ApplicantRefundReceiptViewSet, basename="applicant-refund-receipt")
applicant_router.register("documents", ApplicantDocumentViewSet, basename="applicant-document")
applicant_router.register("notes", ApplicantNoteViewSet, basename="applicant-note")
applicant_router.register("status-history", ApplicantStatusHistoryViewSet, basename="applicant-status-history")

# Agreement Template Nesting
agreement_template_router = NestedDefaultRouter(router, "agreement-templates", lookup="template")
agreement_template_router.register("clauses", AgreementTemplateClauseViewSet, basename="agreement-template-clause")


# ==========================================
# 3. GRANDCHILD ROUTERS (Level 2 Nesting)
# ==========================================

# Visa -> Jobs -> Facilities
job_router = NestedDefaultRouter(visa_router, "jobs", lookup="job")
job_router.register("facilities", JobFacilityViewSet, basename="job-facility")


# ==========================================
# 4. URLPATTERNS REGISTRATION
# ==========================================
urlpatterns = [
    # JWT Authentication Endpoints
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", UserProfileAPIView.as_view(), name="auth-me"),
    path("auth/me/password/", UserPasswordUpdateAPIView.as_view(), name="auth-me-password"),
    path(
        "schema/",
        SpectacularAPIView.as_view(),
        name="api-schema",
    ),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(
            url_name="api-schema",
        ),
        name="api-docs",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(
            url_name="api-schema",
        ),
        name="api-redoc",
    ),
    path(
        "public/applicant-status/",
        PublicApplicantStatusCheckAPIView.as_view(),
        name="public-applicant-status",
    ),
    path(
        "public/staff-slots/current-month/",
        PublicCurrentMonthStaffSlotListAPIView.as_view(),
        name="public-current-month-staff-slots",
    ),
    path(
        "public/staff-profiles/access/",
        PublicStaffProfileAccessAPIView.as_view(),
        name="public-staff-profile-access",
    ),
    path(
        "public/applicant-results/current-month/",
        PublicCurrentMonthApplicantResultListAPIView.as_view(),
        name="public-current-month-applicant-results",
    ),
    path("", include(router.urls)),
    path("", include(country_router.urls)),
    path("", include(visa_router.urls)),
    path("", include(job_router.urls)),
    path("", include(staff_router.urls)),
    path("", include(sub_staff_router.urls)),
    path("", include(applicant_router.urls)),
    path("", include(agreement_template_router.urls)),
]

