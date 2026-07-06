from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view


PUBLIC_READ_ADMIN_WRITE = (
    "Public users can read this resource. Authenticated admin/staff users can "
    "create, update, and delete it from the management panel."
)
ADMIN_ONLY = (
    "Authenticated admin/staff endpoint. This resource is hidden from public "
    "frontend users and is intended for internal management workflows."
)
READ_ONLY_ADMIN_CONTROLLED = (
    "Authenticated admin/staff endpoint. Records are generated or controlled by "
    "service workflows and should be reviewed rather than freely edited."
)


def crud_schema(tag, plural_name, singular_name=None, description=ADMIN_ONLY):
    singular_name = singular_name or plural_name.rstrip("s")

    return extend_schema_view(
        list=extend_schema(
            tags=[tag],
            summary=f"List {plural_name}",
            description=description,
        ),
        retrieve=extend_schema(
            tags=[tag],
            summary=f"Retrieve {singular_name}",
            description=description,
        ),
        create=extend_schema(
            tags=[tag],
            summary=f"Create {singular_name}",
            description=description,
        ),
        update=extend_schema(
            tags=[tag],
            summary=f"Replace {singular_name}",
            description=description,
        ),
        partial_update=extend_schema(
            tags=[tag],
            summary=f"Update {singular_name}",
            description=description,
        ),
        destroy=extend_schema(
            tags=[tag],
            summary=f"Delete {singular_name}",
            description=description,
        ),
    )


def read_only_schema(tag, plural_name, singular_name=None, description=READ_ONLY_ADMIN_CONTROLLED):
    singular_name = singular_name or plural_name.rstrip("s")

    return extend_schema_view(
        list=extend_schema(
            tags=[tag],
            summary=f"List {plural_name}",
            description=description,
        ),
        retrieve=extend_schema(
            tags=[tag],
            summary=f"Retrieve {singular_name}",
            description=description,
        ),
    )


def notice_schema():
    notice_description = (
        "Public notice board resource. Public users can read active notice "
        "records. Authenticated admin/staff users can create, update, pin, "
        "publish/unpublish, and attach an optional PDF or image file. For file "
        "uploads, send multipart/form-data with the attachment field."
    )

    return extend_schema_view(
        list=extend_schema(
            tags=["Agency"],
            summary="List notices",
            description=notice_description,
        ),
        retrieve=extend_schema(
            tags=["Agency"],
            summary="Retrieve notice",
            description=notice_description,
        ),
        create=extend_schema(
            tags=["Agency"],
            summary="Create notice with optional attachment",
            description=notice_description,
            examples=[
                OpenApiExample(
                    "Create notice metadata",
                    value={
                        "title": "Office closed for public holiday",
                        "content": "Our office will remain closed tomorrow.",
                        "is_pinned": True,
                        "is_active": True,
                    },
                    request_only=True,
                ),
            ],
        ),
        update=extend_schema(
            tags=["Agency"],
            summary="Replace notice with optional attachment",
            description=notice_description,
        ),
        partial_update=extend_schema(
            tags=["Agency"],
            summary="Update notice with optional attachment",
            description=notice_description,
        ),
        destroy=extend_schema(
            tags=["Agency"],
            summary="Delete notice",
            description=notice_description,
        ),
    )
def applicant_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=["Applicants"],
            summary="List applicants",
            description=(
                "Authenticated applicant pipeline list. Supports search, "
                "filtering, ordering, and exposes internal tracking fields for "
                "admin/staff users only."
            ),
        ),
        retrieve=extend_schema(
            tags=["Applicants"],
            summary="Retrieve applicant detail",
            description=(
                "Authenticated applicant detail with profile, addresses, "
                "payments, refunds, documents, notes, and status history."
            ),
        ),
        create=extend_schema(
            tags=["Applicants"],
            summary="Create applicant",
            description=(
                "Creates an applicant, generates the public ARG application ID, "
                "creates the applicant profile, and links all active agreement "
                "templates."
            ),
        ),
        update=extend_schema(
            tags=["Applicants"],
            summary="Replace applicant",
            description="Authenticated full applicant update for admin/staff users.",
        ),
        partial_update=extend_schema(
            tags=["Applicants"],
            summary="Update applicant",
            description="Authenticated partial applicant update for admin/staff users.",
        ),
        destroy=extend_schema(
            tags=["Applicants"],
            summary="Delete applicant",
            description="Authenticated applicant deletion endpoint for admin/staff users.",
        ),
        change_status=extend_schema(
            tags=["Applicants"],
            summary="Change applicant status and send notification",
            description=(
                "Updates an applicant status, records status history, sends the "
                "linked status email via the selected or assigned lawyer sender, "
                "and creates refund records automatically when status becomes "
                "Rejected."
            ),
        ),
        send_email=extend_schema(
            tags=["Applicants"],
            summary="Send manual applicant email",
            description=(
                "Admin/staff tool for sending an email to an applicant by "
                "choosing a predefined email template and lawyer sender."
            ),
        ),
        trigger_send=extend_schema(
            tags=["Applicants"],
            summary="Trigger applicant email dispatch",
            description=(
                "Admin/staff email dispatch endpoint accepting applicant, "
                "template, and sender identifiers."
            ),
        ),
    )


def applicant_refund_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=["Finance"],
            summary="List applicant refunds",
            description="Authenticated refund records for an applicant.",
        ),
        retrieve=extend_schema(
            tags=["Finance"],
            summary="Retrieve applicant refund",
            description="Authenticated refund detail for an applicant.",
        ),
        create=extend_schema(
            tags=["Finance"],
            summary="Generate applicant refund",
            description=(
                "Generates a refund for an eligible rejected applicant using the "
                "configured rule: first installment is non-refundable; second "
                "and third installments are 80% refundable."
            ),
        ),
        summary=extend_schema(
            tags=["Finance"],
            summary="Get applicant refund summary",
            description="Returns payment totals, refundable totals, and latest refund details.",
        ),
    )


def apply_schema_overrides(**viewsets):
    public_content = {
        "CountryViewSet": ("Countries", "countries", "country"),
        "CountryRequirementViewSet": ("Countries", "country requirements", "country requirement"),
        "CountryFAQViewSet": ("Countries", "country FAQs", "country FAQ"),
        "CountryGalleryViewSet": ("Countries", "country gallery items", "country gallery item"),
        "VisaCategoryViewSet": ("Visas", "visa categories", "visa category"),
        "VisaViewSet": ("Visas", "visas", "visa"),
        "VisaRequirementViewSet": ("Visas", "visa requirements", "visa requirement"),
        "VisaStepViewSet": ("Visas", "visa steps", "visa step"),
        "VisaFAQViewSet": ("Visas", "visa FAQs", "visa FAQ"),
        "VisaSEOViewSet": ("Visas", "visa SEO records", "visa SEO record"),
        "VisaJobViewSet": ("Visas", "visa jobs", "visa job"),
        "JobFacilityViewSet": ("Visas", "job facilities", "job facility"),
        "AgencyServiceViewSet": ("Agency", "agency services", "agency service"),
        "CompanyInformationViewSet": ("Agency", "company information records", "company information record"),
        "OfficeViewSet": ("Agency", "branches", "branch"),
        "SocialLinkViewSet": ("Agency", "social links", "social link"),
        "ReviewViewSet": ("Agency", "reviews", "review"),
    }

    admin_crud = {
        "ContactUsViewSet": ("Agency", "contact submissions", "contact submission"),
        "EmailTemplateViewSet": ("Agency", "email templates", "email template"),
        "LawyerViewSet": ("Agency", "lawyer senders", "lawyer sender"),
        "DesignationViewSet": ("Staff", "designations", "designation"),
        "StaffViewSet": ("Staff", "staff members", "staff member"),
        "StaffMonthlySlotViewSet": ("Staff", "staff monthly slots", "staff monthly slot"),
        "StaffPublicProfileViewSet": ("Staff", "staff public profile settings", "staff public profile setting"),
        "StaffDocumentViewSet": ("Staff", "staff documents", "staff document"),
        "StaffEmergencyContactViewSet": ("Staff", "staff emergency contacts", "staff emergency contact"),
        "ApplicationStatusViewSet": ("Applicants", "application statuses", "application status"),
        "ApplicantTagViewSet": ("Applicants", "applicant tags", "applicant tag"),
        "AgreementTemplateViewSet": ("Agreements", "agreement templates", "agreement template"),
        "AgreementTemplateClauseViewSet": ("Agreements", "agreement template clauses", "agreement template clause"),
        "CurrencyRateViewSet": ("Finance", "currency rates", "currency rate"),
        "ApplicantAddressViewSet": ("Applicants", "applicant addresses", "applicant address"),
        "ApplicantPaymentViewSet": ("Finance", "applicant payments", "applicant payment"),
        "ApplicantRefundBankDetailViewSet": ("Finance", "refund bank details", "refund bank detail"),
        "ApplicantDocumentViewSet": ("Applicants", "applicant documents", "applicant document"),
        "ApplicantNoteViewSet": ("Applicants", "applicant notes", "applicant note"),
    }

    admin_read = {
        "ApplicantMoneyReceiptViewSet": ("Finance", "money receipts", "money receipt"),
        "ApplicantRefundReceiptViewSet": ("Finance", "refund receipts", "refund receipt"),
        "ApplicantStatusHistoryViewSet": ("Applicants", "status history entries", "status history entry"),
    }

    if "NoticeViewSet" in viewsets:
        notice_schema()(viewsets["NoticeViewSet"])

    for name, args in public_content.items():
        if name in viewsets:
            crud_schema(*args, description=PUBLIC_READ_ADMIN_WRITE)(viewsets[name])

    for name, args in admin_crud.items():
        if name in viewsets:
            crud_schema(*args, description=ADMIN_ONLY)(viewsets[name])

    for name, args in admin_read.items():
        if name in viewsets:
            read_only_schema(*args, description=READ_ONLY_ADMIN_CONTROLLED)(viewsets[name])

    if "ApplicantViewSet" in viewsets:
        applicant_schema()(viewsets["ApplicantViewSet"])

    if "ApplicantRefundViewSet" in viewsets:
        applicant_refund_schema()(viewsets["ApplicantRefundViewSet"])


