from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from routing.models import FuelStation
from routing.services.fuel_optimizer import optimize_fuel_stops


class FuelOptimizerTests(TestCase):
	def test_chooses_reachable_low_cost_stops(self):
		stations = [
			{"id": 1, "name": "Cheap", "price": 3, "distance_from_start": 250},
			{"id": 2, "name": "Expensive", "price": 5, "distance_from_start": 400},
			{"id": 3, "name": "Finish", "price": 0, "distance_from_start": 650},
		]

		result = optimize_fuel_stops(
			[{"distance_from_start": 0, "price": 4}] + stations
		)

		self.assertEqual([station.get("name") for station in result["stops"]], [
			None, "Cheap", "Finish"
		])
		self.assertEqual(result["total_cost"], 220)


class RouteApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		FuelStation.objects.create(
			name="Route Fuel",
			price=3,
			latitude=40,
			longitude=-94,
			geocoded=True,
		)

	def test_route_endpoint_returns_json_in_browser(self):
		response = self.client.get("/api/route/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["example"]["start"]["lat"], 37.7749)

	@patch("routing.views.get_route")
	def test_returns_route_and_fuel_summary(self, get_route):
		get_route.return_value = {
			"distance": 650 * 1609.344,
			"duration": 180 * 60,
			"geometry": {
				"type": "LineString",
				"coordinates": [[-100, 40], [-88, 40]],
			},
		}

		response = self.client.post(
			"/api/route/",
			{
				"start": {"lat": 40, "lon": -100},
				"finish": {"lat": 40, "lon": -96},
			},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["route"]["distance_miles"], 650)
		self.assertEqual(response.data["fuel_summary"]["total_gallons"], 65)
		self.assertEqual(response.data["fuel_summary"]["total_cost"], 195)
		self.assertEqual(len(response.data["fuel_stops"]), 1)
		get_route.assert_called_once()

	def test_root_serves_map_page(self):
		response = self.client.get("/")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Fuel Route Planner")

	@patch("routing.views.get_route")
	def test_uses_imported_price_when_route_needs_no_stop(self, get_route):
		get_route.return_value = {
			"distance": 300 * 1609.344,
			"duration": 180 * 60,
			"geometry": {
				"type": "LineString",
				"coordinates": [[-100, 40], [-96, 40]],
			},
		}

		response = self.client.post(
			"/api/route/",
			{
				"start": {"lat": 40, "lon": -100},
				"finish": {"lat": 40, "lon": -96},
			},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["fuel_stops"], [])
		self.assertEqual(response.data["fuel_summary"]["total_cost"], 90)
