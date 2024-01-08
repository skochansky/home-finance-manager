from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts_management.urls")),
    path("analysis/", include("budget_analysis.urls")),
]
