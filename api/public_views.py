from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from applicant.selectors import (
    get_public_applicant_status,
    get_public_current_month_applicant_results,
)
from staff.selectors import (
    get_public_current_month_staff_slots,
    get_public_staff_profile_by_slug,
)

from .public_serializers import (
    PublicApplicantResultSerializer,
    PublicApplicantStatusCheckSerializer,
    PublicApplicantStatusSerializer,
    PublicStaffMonthlySlotSerializer,
    PublicStaffProfileAccessSerializer,
    PublicStaffProfileSerializer,
)


class PublicApplicantStatusCheckAPIView(APIView):
    permission_classes = [
        AllowAny,
    ]

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

    def get(self, request):
        slots = get_public_current_month_staff_slots()

        return Response(
            PublicStaffMonthlySlotSerializer(
                slots,
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

    def post(self, request, slug):
        serializer = PublicStaffProfileAccessSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        public_profile = get_public_staff_profile_by_slug(
            slug,
        )

        if public_profile is None:
            return Response(
                {
                    "detail": "No public staff profile was found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not public_profile.check_public_password(
            serializer.validated_data["password"],
        ):
            return Response(
                {
                    "detail": "Invalid public profile password."
                },
                status=status.HTTP_403_FORBIDDEN,
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

    def get(self, request):
        applicants = get_public_current_month_applicant_results()

        return Response(
            PublicApplicantResultSerializer(
                applicants,
                many=True,
            ).data,
            status=status.HTTP_200_OK,
        )
