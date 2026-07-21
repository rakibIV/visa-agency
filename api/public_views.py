from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema

from applicant.selectors import (
    get_public_applicant_status,
    get_public_current_month_applicant_results,
)
from staff.selectors import (
    get_public_current_month_staff_slots,
    get_public_staff_profile_by_credentials,
)

from .public_serializers import (
    PublicApplicantResultSerializer,
    PublicApplicantStatusCheckSerializer,
    PublicApplicantStatusSerializer,
    PublicApplicationRequestSerializer,
    PublicContactUsSerializer,
    PublicStaffMonthlySlotSerializer,
    PublicStaffProfileAccessSerializer,
    PublicStaffProfileSerializer,
)


class PublicApplicantStatusCheckAPIView(APIView):
    permission_classes = [
        AllowAny,
    ]

    @extend_schema(
        tags=["Public"],
        summary="Check applicant status",
        description=(
            "Public applicant tracking endpoint. A visitor submits the public "
            "business application ID, email address, and phone number. If all "
            "three values match, the API returns safe tracking data only."
        ),
        request=PublicApplicantStatusCheckSerializer,
        responses={
            200: PublicApplicantStatusSerializer,
            404: OpenApiResponse(
                description="No matching applicant was found.",
            ),
        },
        examples=[
            OpenApiExample(
                "Status check request",
                value={
                    "application_id": "ARGA72Q9",
                    "email": "client@example.com",
                    "phone": "01700000000",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = PublicApplicantStatusCheckSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        applicant = get_public_applicant_status(
            **serializer.validated_data,
        )

        if applicant is None:
            return Response(
                {
                    "detail": "No matching applicant was found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            PublicApplicantStatusSerializer(
                applicant,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


class PublicCurrentMonthStaffSlotListAPIView(APIView):
    permission_classes = [
        AllowAny,
    ]

    @extend_schema(
        tags=["Public"],
        summary="List current-month staff slots",
        description=(
            "Public staff slot leaderboard for the current month. Only active "
            "staff with an enabled public profile and public profile password "
            "are shown."
        ),
        responses={
            200: PublicStaffMonthlySlotSerializer(many=True),
        },
    )
    def get(self, request):
        from django.utils import timezone
        from django.db.models import Prefetch, Count
        from staff.models import Staff, StaffMonthlySlot
        
        month_start = timezone.localdate().replace(day=1)
        slots = StaffMonthlySlot.objects.filter(allocation_month=month_start).annotate(
            used_slot_count=Count('applicants')
        )
        staff_qs = Staff.objects.filter(is_active=True).prefetch_related(
            Prefetch('monthly_slots', queryset=slots, to_attr='current_month_slots')
        )

        return Response(
            PublicStaffMonthlySlotSerializer(
                staff_qs,
                many=True,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


class PublicStaffProfileAccessAPIView(APIView):
    permission_classes = [
        AllowAny,
    ]

    @extend_schema(
        tags=["Public"],
        summary="Unlock a protected public staff profile",
        description=(
            "A visitor submits the exact public profile password for the staff "
            "slug. If valid, the API returns the configured public profile "
            "fields plus current-month and lifetime slot statistics."
        ),
        request=PublicStaffProfileAccessSerializer,
        responses={
            200: PublicStaffProfileSerializer,
            403: OpenApiResponse(
                description="Invalid public profile password.",
            ),
            404: OpenApiResponse(
                description="No public staff profile was found.",
            ),
        },
        examples=[
            OpenApiExample(
                "Profile access request",
                value={
                    "employee_id": "EMP-1001",
                    "password": "visitor-password",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = PublicStaffProfileAccessSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        public_profile = get_public_staff_profile_by_credentials(
            serializer.validated_data["employee_id"],
        )

        if public_profile is None:
            raise ValidationError(
                {"detail": "Profile not found or not active."}
            )

        if not public_profile.staff.user.check_password(
            serializer.validated_data["password"]
        ):
            raise ValidationError(
                {"detail": "Incorrect password."}
            )

        return Response(
            PublicStaffProfileSerializer(
                public_profile,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


class PublicCurrentMonthApplicantResultListAPIView(APIView):
    permission_classes = [
        AllowAny,
    ]

    @extend_schema(
        tags=["Public"],
        summary="List current-month approved/rejected applicant results",
        description=(
            "Public live visa update feed for applicants approved or rejected "
            "in the current month. Applicant names are masked for privacy."
        ),
        responses={
            200: PublicApplicantResultSerializer(many=True),
        },
    )
    def get(self, request):
        applicants = get_public_current_month_applicant_results()

        from applicant.models import FakeLiveResult
        from django.utils import timezone
        today = timezone.localdate()
        start_date = today - timezone.timedelta(days=90)
        
        fake_results = FakeLiveResult.objects.filter(
            result_date__date__gte=start_date,
            result_date__date__lte=today,
        ).select_related(
            "visa",
            "visa__country",
            "job",
            "status",
        )

        combined = list(applicants) + list(fake_results)
        combined.sort(key=lambda x: getattr(x, "result_date", None) or getattr(x, "updated_at", None), reverse=True)

        return Response(
            PublicApplicantResultSerializer(
                combined,
                many=True,
            ).data,
            status=status.HTTP_200_OK,
        )



class PublicApplicationRequestCreateAPIView(CreateAPIView):
    serializer_class = PublicApplicationRequestSerializer
    permission_classes = [AllowAny]


class PublicContactUsCreateAPIView(CreateAPIView):
    serializer_class = PublicContactUsSerializer
    permission_classes = [AllowAny]
