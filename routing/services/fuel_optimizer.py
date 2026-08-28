MAX_RANGE = 500
MPG = 10


def optimize_fuel_stops(stations):
    """
    Find the minimum-cost sequence of fuel stops.

    stations must be sorted by distance_from_start.

    The first item represents the starting point.
    The last item represents the destination.
    """

    n = len(stations)

    dp = [float("inf")] * n
    previous = [None] * n

    dp[0] = 0

    for i in range(n):

        if dp[i] == float("inf"):
            continue

        for j in range(i + 1, n):

            distance = (
                stations[j]["distance_from_start"]
                - stations[i]["distance_from_start"]
            )

            if distance > MAX_RANGE:
                break

            gallons = distance / MPG

            fuel_price = stations[i].get("price", 0)

            cost = gallons * fuel_price

            new_cost = dp[i] + cost

            if new_cost < dp[j]:
                dp[j] = new_cost
                previous[j] = i

    if dp[-1] == float("inf"):
        raise ValueError(
            "Destination cannot be reached with available fuel stations"
        )

    path = []

    current = n - 1

    while current is not None:
        path.append(stations[current])
        current = previous[current]

    path.reverse()

    return {
        "total_cost": dp[-1],
        "stops": path,
    }