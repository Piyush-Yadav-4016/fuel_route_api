import requests


OSRM_URL = "https://router.project-osrm.org/route/v1/driving"


def get_route(
    start_lon,
    start_lat,
    finish_lon,
    finish_lat,
):

    coordinates = (
        f"{start_lon},{start_lat};"
        f"{finish_lon},{finish_lat}"
    )

    url = f"{OSRM_URL}/{coordinates}"

    params = {
        "overview": "full",
        "geometries": "geojson",
    }

    response = requests.get(
        url,
        params=params,
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    if data["code"] != "Ok":
        raise ValueError("Unable to calculate route")

    return data["routes"][0]