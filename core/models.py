from django.db import models
from uuid import uuid4

# Create your models here.
class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(BaseModel):
    is_deleted = models.BooleanField(default=False)

    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        abstract = True


class Currency(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True, help_text="ISO currency code (e.g. USD, EUR, BDT)")
    symbol = models.CharField(max_length=10, blank=True, help_text="Currency symbol (e.g. $, €, ৳)")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Currencies"

    def __str__(self):
        return f"{self.name} ({self.code})"