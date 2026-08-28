from django.contrib import admin
from django.urls import include, path

from routing.views import map_view


urlpatterns = [
    path("", map_view),
    path("admin/", admin.site.urls),
    path("api/", include("routing.urls")),
]