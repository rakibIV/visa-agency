from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import (
    OrderingFilter,
    SearchFilter,
)
from rest_framework.viewsets import ModelViewSet

from .filters import StaffFilter
from .models import (
    Designation,
    Staff,
    StaffMonthlySlot,
    StaffDocument,
    StaffEmergencyContact,
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
        serializer.save(
            staff_id=self.kwargs.get("staff_pk"),
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
