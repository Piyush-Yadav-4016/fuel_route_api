from math import asin, cos, radians, sin, sqrt

from routing.models import FuelStation


EARTH_RADIUS_MILES = 3958.8
ROUTE_SEARCH_MILES = 25


def _distance_miles(first, second):
    latitude_one, longitude_one = map(radians, first)
    latitude_two, longitude_two = map(radians, second)
    delta_latitude = latitude_two - latitude_one
    delta_longitude = longitude_two - longitude_one
    value = (
        sin(delta_latitude / 2) ** 2
        + cos(latitude_one)
        * cos(latitude_two)
        * sin(delta_longitude / 2) ** 2
    )
    return 2 * EARTH_RADIUS_MILES * asin(sqrt(value))


def _closest_route_distance(point, route_coordinates):
    closest_distance = float("inf")
    distance_from_start = 0

    for index, coordinate in enumerate(route_coordinates):
        route_point = (coordinate[1], coordinate[0])
        if not index:
            closest_distance = min(closest_distance, _distance_miles(point, route_point))
            continue

        previous = route_coordinates[index - 1]
        previous_point = (previous[1], previous[0])
        segment_length = _distance_miles(previous_point, route_point)
        latitude_scale = cos(radians((previous_point[0] + route_point[0]) / 2))
        x_length = (route_point[1] - previous_point[1]) * latitude_scale
        y_length = route_point[0] - previous_point[0]
        x_point = (point[1] - previous_point[1]) * latitude_scale
        y_point = point[0] - previous_point[0]
        denominator = x_length * x_length + y_length * y_length
        fraction = 0 if not denominator else (
            (x_point * x_length + y_point * y_length) / denominator
        )
        fraction = max(0, min(1, fraction))
        projected = (
            previous_point[0] + fraction * (route_point[0] - previous_point[0]),
            previous_point[1] + fraction * (route_point[1] - previous_point[1]),
        )
        closest_distance = min(closest_distance, _distance_miles(point, projected))
        distance_from_start += fraction * segment_length

    return closest_distance, distance_from_start


def stations_along_route(route_geometry):
    coordinates = route_geometry["coordinates"]
    candidates = []

    for station in FuelStation.objects.filter(
        geocoded=True,
        latitude__isnull=False,
        longitude__isnull=False,
    ).iterator():
        distance, distance_from_start = _closest_route_distance(
            (station.latitude, station.longitude),
            coordinates,
        )
        if distance <= ROUTE_SEARCH_MILES:
            candidates.append(
                {
                    "id": station.id,
                    "name": station.name,
                    "address": station.address,
                    "city": station.city,
                    "state": station.state,
                    "latitude": station.latitude,
                    "longitude": station.longitude,
                    "price": station.price,
                    "distance_from_start": distance_from_start,
                }
            )

    return sorted(candidates, key=lambda station: station["distance_from_start"])