from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import (
    OrderingFilter,
    SearchFilter,
)
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from django.db.models import F, Count

from .filters import StaffFilter
from .models import (
    Designation,
    Staff,
    StaffMonthlySlot,
    StaffPublicProfile,
    StaffDocument,
    StaffEmergencyContact,
    SubStaff,
    SubStaffMonthlySlot,
)
from .permissions import IsAdminOrReadOnly
from .selectors import (
    get_active_staff,
    get_staff_queryset,
)
from .serializers import (
    DesignationSerializer,
    StaffSerializer,
    StaffDetailSerializer,
    StaffCreateUpdateSerializer,
    StaffMonthlySlotSerializer,
    StaffDocumentSerializer,
    StaffEmergencyContactSerializer,
    SubStaffSerializer,
    SubStaffMonthlySlotSerializer,
)


class DesignationViewSet(ModelViewSet):
    queryset = Designation.objects.all()

    serializer_class = DesignationSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "name",
    ]

    ordering_fields = [
        "display_order",
        "name",
        "created_at",
    ]

    ordering = [
        "display_order",
        "name",
    ]


class StaffViewSet(ModelViewSet):
    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = StaffFilter

    search_fields = [
        "employee_id",
        "user__first_name",
        "user__last_name",
        "phone",
        "nid_number",
        "passport_number",
    ]

    ordering_fields = [
        "employee_id",
        "joining_date",
        "created_at",
    ]

    ordering = [
        "employee_id",
    ]

    def get_queryset(self):
        if (
            self.request.user.is_authenticated
            and self.request.user.is_staff
        ):
            return get_staff_queryset()

        return get_active_staff()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StaffDetailSerializer

        if self.action in [
            "create",
            "update",
            "partial_update",
        ]:
            return StaffCreateUpdateSerializer

        return StaffSerializer


class StaffMonthlySlotViewSet(ModelViewSet):
    serializer_class = StaffMonthlySlotSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_fields = [
        "allocation_month",
    ]

    ordering_fields = [
        "allocation_month",
        "total_slot",
    ]

    ordering = [
        "-allocation_month",
    ]

    def get_queryset(self):
        queryset = (
            StaffMonthlySlot.objects.select_related(
                "staff",
            )
            .annotate(
                remaining_slot=F("total_slot") - Count("applicants"),
            )
            .order_by(
                "-allocation_month",
            )
        )

        staff_pk = self.kwargs.get(
            "staff_pk",
        )

        if staff_pk:
            queryset = queryset.filter(
                staff_id=staff_pk,
            )

        return queryset

    def perform_create(self, serializer):
        staff_pk = self.kwargs.get("staff_pk")
        allocation_month = serializer.validated_data.get("allocation_month")
        
        if StaffMonthlySlot.objects.filter(staff_id=staff_pk, allocation_month=allocation_month).exists():
            raise serializers.ValidationError(
                {"allocation_month": ["A slot for this month already exists for this staff."]}
            )
            
        serializer.save(
            staff_id=staff_pk,
        )


class SubStaffViewSet(ModelViewSet):
    serializer_class = SubStaffSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    ordering_fields = [
        "name",
        "created_at",
    ]

    ordering = [
        "name",
    ]

    def get_queryset(self):
        queryset = SubStaff.objects.select_related(
            "parent_staff",
            "parent_staff__user",
        )

        staff_pk = self.kwargs.get(
            "staff_pk",
        )

        if staff_pk:
            queryset = queryset.filter(
                parent_staff_id=staff_pk,
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            parent_staff_id=self.kwargs.get("staff_pk"),
        )


class SubStaffMonthlySlotViewSet(ModelViewSet):
    serializer_class = SubStaffMonthlySlotSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_fields = [
        "allocation_month",
    ]

    ordering_fields = [
        "allocation_month",
        "allocated_slot",
    ]

    ordering = [
        "-allocation_month",
    ]

    def get_queryset(self):
        queryset = SubStaffMonthlySlot.objects.select_related(
            "sub_staff",
            "sub_staff__parent_staff",
        ).order_by(
            "-allocation_month",
        )

        sub_staff_pk = self.kwargs.get(
            "sub_staff_pk",
        )

        if sub_staff_pk:
            queryset = queryset.filter(
                sub_staff_id=sub_staff_pk,
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            sub_staff_id=self.kwargs.get("sub_staff_pk"),
        )





class StaffDocumentViewSet(ModelViewSet):
    serializer_class = StaffDocumentSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    ordering_fields = [
        "display_order",
        "created_at",
    ]

    ordering = [
        "display_order",
    ]

    def get_queryset(self):
        queryset = (
            StaffDocument.objects.select_related(
                "staff",
            )
            .order_by(
                "display_order",
            )
        )

        staff_pk = self.kwargs.get(
            "staff_pk",
        )

        if staff_pk:
            queryset = queryset.filter(
                staff_id=staff_pk,
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            staff_id=self.kwargs.get("staff_pk"),
        )


class StaffEmergencyContactViewSet(ModelViewSet):
    serializer_class = StaffEmergencyContactSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    ordering_fields = [
        "name",
        "created_at",
    ]

    ordering = [
        "name",
    ]

    def get_queryset(self):
        queryset = (
            StaffEmergencyContact.objects.select_related(
                "staff",
            )
            .order_by(
                "name",
            )
        )

        staff_pk = self.kwargs.get(
            "staff_pk",
        )

        if staff_pk:
            queryset = queryset.filter(
                staff_id=staff_pk,
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            staff_id=self.kwargs.get("staff_pk"),
        )
