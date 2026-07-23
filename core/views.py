from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Currency
from .serializers import CurrencySerializer
from applicant.permissions import IsAdminOrReadOnly

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAdminOrReadOnly]
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    
    filterset_fields = ["is_active"]
    search_fields = ["name", "code", "symbol"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["name"]
