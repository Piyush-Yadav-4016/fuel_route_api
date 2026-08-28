from django.urls import path

from routing.views import calculate_route, map_view


urlpatterns = [

    path(
        "route/",
        calculate_route
    ),

    path(
        "map/",
        map_view
    ),

]