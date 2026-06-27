from country.views import (
    CountryListAPIView,
    CountryDetailAPIView,
    CountryCreateAPIView,
    CountryUpdateAPIView,
    CountryDeleteAPIView,
)


from django.urls import path

urlpatterns = [
    path(
        "countries/",
        CountryListAPIView.as_view(),
        name="country-list",
    ),
    path(
        "countries/<slug:slug>/",
        CountryDetailAPIView.as_view(),
        name="country-detail",
    ),
    path(
        "countries/create/",
        CountryCreateAPIView.as_view(),
        name="country-create",
    ),
    path(
        "countries/<uuid:pk>/update/",
        CountryUpdateAPIView.as_view(),
        name="country-update",
    ),
    path(
        "countries/<uuid:pk>/delete/",
        CountryDeleteAPIView.as_view(),
        name="country-delete",
    ),
]