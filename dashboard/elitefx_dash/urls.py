"""URL root — panels zote ni za monitor app (read-only). Admin = internal ops tu."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("monitor.urls")),
]
