from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render

from routing.models import FuelStation
from routing.services.fuel_optimizer import MPG, optimize_fuel_stops
from routing.services.fuel_route import stations_along_route
from routing.services.router import get_route


def map_view(request):
    return render(
        request,
        "routing/map.html"
    )

@api_view(["GET", "POST"])

def calculate_route(request):

    if request.method == "GET":
        return Response(
            {
                "message": "Send a POST request with start and finish coordinates.",
                "example": {
                    "start": {"lat": 37.7749, "lon": -122.4194},
                    "finish": {"lat": 34.0522, "lon": -118.2437},
                },
            }
        )

    start = request.data.get("start")
    finish = request.data.get("finish")
    
    if not start or not finish:
        return Response(
            {
                "error": "start and finish are required"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not isinstance(start, dict) or not isinstance(finish, dict):
        return Response(
            {
                "error": "start and finish must be objects"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    start_lat = start.get("lat")
    start_lon = start.get("lon")

    finish_lat = finish.get("lat")
    finish_lon = finish.get("lon")

    if None in (
        start_lat,
        start_lon,
        finish_lat,
        finish_lon,
    ):
        return Response(
            {
                "error": "lat and lon are required"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        values = [
            float(start_lat),
            float(start_lon),
            float(finish_lat),
            float(finish_lon),
        ]
        if not -90 <= values[0] <= 90 or not -90 <= values[2] <= 90:
            raise ValueError("latitude must be between -90 and 90")
        if not -180 <= values[1] <= 180 or not -180 <= values[3] <= 180:
            raise ValueError("longitude must be between -180 and 180")
        if not all(
            18.9 <= values[index] <= 71.5
            and -179.2 <= values[index + 1] <= -66.9
            for index in (0, 2)
        ):
            raise ValueError("start and finish must be within the USA")

        route = get_route(
            values[1],
            values[0],
            values[3],
            values[2],
        )
        distance_miles = route["distance"] / 1609.344
        stations = stations_along_route(route["geometry"])
        cheapest_station = FuelStation.objects.order_by("price").first()
        starting_price = (
            stations[0]["price"]
            if stations
            else cheapest_station.price if cheapest_station else 0
        )
        plan = optimize_fuel_stops(
            [{"distance_from_start": 0, "price": starting_price}]
            + stations
            + [{"distance_from_start": distance_miles, "price": 0}]
        )

    except Exception as exc:

        return Response(
            {
                "error": str(exc)
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    duration_minutes = route["duration"] / 60
    selected_stops = [
        stop for stop in plan["stops"] if stop.get("id") is not None
    ]

    response_data = {
        "start": {
            "latitude": start_lat,
            "longitude": start_lon,
        },

        "finish": {
            "latitude": finish_lat,
            "longitude": finish_lon,
        },

        "route": {
            "distance_miles": round(distance_miles, 2),
            "duration_minutes": round(duration_minutes),
            "geometry": route["geometry"],
        },

        "vehicle": {
            "max_range_miles": 500,
            "fuel_economy_mpg": 10,
        },

        "fuel_stops": selected_stops,

        "fuel_summary": {
            "total_distance_miles": round(distance_miles, 2),
            "total_gallons": round(distance_miles / MPG, 2),
            "total_cost": round(plan["total_cost"], 2),
        },
    }

    return Response(response_data)