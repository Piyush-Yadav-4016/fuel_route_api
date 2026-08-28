MPG = 10


def calculate_fuel_cost(distance_miles, fuel_price):
    """
    Calculate fuel required and total fuel cost.
    """

    gallons_used = distance_miles / MPG

    total_cost = gallons_used * fuel_price

    return {
        "distance_miles": distance_miles,
        "gallons_used": gallons_used,
        "fuel_price": fuel_price,
        "total_cost": total_cost,
    }