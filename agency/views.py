from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminOrStaff

from .filters import AgencyServiceFilter
from .models import (
    AgencyService,
    CompanyInformation,
    ContactUs,
    Office,
    SocialLink,
    EmailTemplate,
    Lawyer,
    Notice,
    Review,
    ApplicationRequest,
)
from .permissions import IsAdminOrReadOnly
from .serializers import (
    AgencyServiceSerializer,
    CompanyInformationSerializer,
    CompanyInformationDetailSerializer,
    ContactUsSerializer,
    OfficeSerializer,
    SocialLinkSerializer,
    EmailTemplateSerializer,
    LawyerSerializer,
    NoticeSerializer,
    ReviewSerializer,
    ApplicationRequestSerializer,
)


class AgencyServiceViewSet(ModelViewSet):
    queryset = AgencyService.objects.all()

    serializer_class = AgencyServiceSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = AgencyServiceFilter

    search_fields = [
        "title",
    ]

    ordering_fields = [
        "title",
        "display_order",
        "created_at",
    ]

    ordering = [
        "display_order",
        "title",
    ]


class NoticeViewSet(ModelViewSet):
    queryset = Notice.objects.all()

    serializer_class = NoticeSerializer

    parser_classes = [
        JSONParser,
        MultiPartParser,
        FormParser,
    ]

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "title",
        "content",
    ]

    ordering_fields = [
        "title",
        "is_pinned",
        "created_at",
    ]

    ordering = [
        "-is_pinned",
        "-created_at",
    ]


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()

    serializer_class = ReviewSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "name",
        "comment",
    ]

    ordering_fields = [
        "created_at",
        "rating",
    ]

    ordering = [
        "-created_at",
    ]


class ContactUsViewSet(ModelViewSet):
    queryset = ContactUs.objects.all()

    serializer_class = ContactUsSerializer

    permission_classes = [
        IsAdminOrStaff,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "is_read",
        "is_active",
    ]

    search_fields = [
        "name",
        "email",
        "subject",
        "message",
    ]

    ordering_fields = [
        "created_at",
        "is_read",
    ]

    ordering = [
        "-created_at",
    ]


from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

class CompanyInformationViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                GenericViewSet):
    queryset = CompanyInformation.objects.all().order_by('-pk')
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_serializer_class(self):
        return CompanyInformationDetailSerializer


class OfficeViewSet(ModelViewSet):
    queryset = Office.objects.all()

    serializer_class = OfficeSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        OrderingFilter,
        SearchFilter,
    ]

    search_fields = [
        "branch_name",
        "address",
    ]

    ordering_fields = [
        "display_order",
        "branch_name",
    ]

    ordering = [
        "display_order",
        "branch_name",
    ]

    def perform_create(self, serializer):
        company = CompanyInformation.objects.first()
        serializer.save(company=company)


class SocialLinkViewSet(ModelViewSet):
    queryset = SocialLink.objects.all()

    serializer_class = SocialLinkSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    ordering = [
        "display_order",
    ]

    def perform_create(self, serializer):
        company = CompanyInformation.objects.first()
        serializer.save(company=company)


def ensure_templates_for_all_statuses():
    """
    Ensures that every ApplicationStatus in the database has a corresponding EmailTemplate.
    """
    from applicant.models import ApplicationStatus
    from agency.models import EmailTemplate

    statuses = ApplicationStatus.objects.all()
    for status_obj in statuses:
        if not EmailTemplate.objects.filter(status=status_obj).exists():
            tmpl_name = f"{status_obj.name} Notification"
            is_rejected = "reject" in status_obj.name.lower()
            is_approved = "approve" in status_obj.name.lower() or "pass" in status_obj.name.lower()

            if is_rejected:
                subject = f"Application Update: {status_obj.name}"
                body = (
                    "<p>Dear <strong style='color: #0f172a;'>{{ applicant_name }}</strong>,</p>"
                    "<p>We regret to inform you that after careful review, your application "
                    "(ID: <strong style='color: #0f172a;'>{{ applicant_id }}</strong>) for "
                    "<strong style='color: #0f172a;'>{{ visa }}</strong> ({{ country }}) has been updated.</p>"
                    "<div class='status-box'>"
                    "  <span class='status-label'>New Application Status</span>"
                    "  <p class='status-value'>{{ current_status }}</p>"
                    "</div>"
                    "<p>Our team is available to discuss your file and explore next steps or alternative solutions.</p>"
                    "<p>Best regards,<br>The {{ company_name }} Team</p>"
                )
            elif is_approved:
                subject = f"Congratulations! Application Status: {status_obj.name}"
                body = (
                    "<p>Dear <strong style='color: #0f172a;'>{{ applicant_name }}</strong>,</p>"
                    "<p>We are delighted to inform you that your application "
                    "(ID: <strong style='color: #0f172a;'>{{ applicant_id }}</strong>) for "
                    "<strong style='color: #0f172a;'>{{ visa }}</strong> ({{ country }}) has been updated.</p>"
                    "<div class='status-box'>"
                    "  <span class='status-label'>New Application Status</span>"
                    "  <p class='status-value'>{{ current_status }}</p>"
                    "</div>"
                    "<p>Our processing team will contact you shortly regarding the next steps.</p>"
                    "<p>Best regards,<br>The {{ company_name }} Team</p>"
                )
            else:
                subject = f"Application Update: {status_obj.name}"
                body = (
                    "<p>Dear <strong style='color: #0f172a;'>{{ applicant_name }}</strong>,</p>"
                    "<p>We are writing to inform you that your application "
                    "(ID: <strong style='color: #0f172a;'>{{ applicant_id }}</strong>) status has been updated.</p>"
                    "<div class='status-box'>"
                    "  <span class='status-label'>New Application Status</span>"
                    "  <p class='status-value'>{{ current_status }}</p>"
                    "</div>"
                    "<p>If you have any questions or require further assistance, please do not hesitate to contact our team.</p>"
                    "<p>Best regards,<br>The {{ company_name }} Team</p>"
                )

            base_name = tmpl_name
            counter = 1
            while EmailTemplate.objects.filter(name=tmpl_name).exists():
                tmpl_name = f"{base_name} ({counter})"
                counter += 1

            EmailTemplate.objects.create(
                name=tmpl_name,
                status=status_obj,
                subject=subject,
                body=body,
                is_active=True,
            )


class EmailTemplateViewSet(ModelViewSet):
    serializer_class = EmailTemplateSerializer

    permission_classes = [
        IsAdminOrStaff,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    def get_queryset(self):
        try:
            ensure_templates_for_all_statuses()
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(f"Error ensuring templates for all statuses: {exc}")

        return (
            EmailTemplate.objects.select_related(
                "status",
            )
            .order_by(
                "status__display_order",
                "name",
            )
        )

    search_fields = [
        "name",
        "subject",
        "body",
        "status__name",
    ]

    ordering_fields = [
        "name",
        "status",
        "created_at",
    ]

    ordering = [
        "name",
    ]


class LawyerViewSet(ModelViewSet):
    serializer_class = LawyerSerializer

    permission_classes = [
        IsAdminOrStaff,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    def get_queryset(self):
        return (
            Lawyer.objects.select_related(
                "country",
            )
            .order_by(
                "-is_default",
                "name",
            )
        )

    search_fields = [
        "name",
        "email",
        "env_key",
        "phone",
        "country__name",
    ]

    ordering_fields = [
        "name",
        "is_default",
        "created_at",
    ]

    ordering = [
        "-is_default",
        "name",
    ]



class ApplicationRequestViewSet(ModelViewSet):
    queryset = ApplicationRequest.objects.all().order_by('-created_at')
    serializer_class = ApplicationRequestSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

from .serializers import AgencyImageSerializer, CompanyLogoSerializer, ImportantNoteSerializer

class AgencyImageViewSet(ModelViewSet):
    serializer_class = AgencyImageSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]
    def get_queryset(self):
        from .models import AgencyImage
        return AgencyImage.objects.all()


class CompanyLogoViewSet(ModelViewSet):
    serializer_class = CompanyLogoSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ["title"]
    ordering_fields = ["serial_number", "created_at"]
    ordering = ["serial_number", "created_at"]

    def get_queryset(self):
        from .models import CompanyLogo
        return CompanyLogo.objects.all().select_related("company")



class ImportantNoteViewSet(ModelViewSet):
    serializer_class = ImportantNoteSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ["title", "content"]
    ordering_fields = ["is_default", "title", "created_at"]
    ordering = ["-is_default", "title"]

    def get_queryset(self):
        from .models import ImportantNote
        return ImportantNote.objects.all()

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class FakeStatsAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        company = CompanyInformation.objects.first()
        if not company:
            return Response({"approved_count": 0, "rejected_count": 0, "processing_count": 0})
        return Response({
            "approved_count": company.manual_approved_count,
            "rejected_count": company.manual_rejected_count,
            "processing_count": company.manual_processing_count,
        })

    def post(self, request, *args, **kwargs):
        company = CompanyInformation.objects.first()
        if not company:
            # Create if it doesn't exist to prevent errors
            company = CompanyInformation.objects.create(company_name="Default Company", address="Default Address", phone="123")
            
        company.manual_approved_count = int(request.data.get("approved_count", 0))
        company.manual_rejected_count = int(request.data.get("rejected_count", 0))
        company.manual_processing_count = int(request.data.get("processing_count", 0))
        company.save()
        
        return Response({
            "approved_count": company.manual_approved_count,
            "rejected_count": company.manual_rejected_count,
            "processing_count": company.manual_processing_count,
        })
        
    def put(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)



