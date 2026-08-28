import time

from django.core.management.base import BaseCommand

from routing.models import FuelStation
from routing.services.geocoder import geocode_address


class Command(BaseCommand):
    help = "Geocode fuel stations using the US Census Geocoder"

    def handle(self, *args, **kwargs):

        stations = FuelStation.objects.filter(
            geocoded=False
        )

        total = stations.count()

        self.stdout.write(
            f"Found {total} stations to geocode."
        )

        for index, station in enumerate(stations, start=1):

            address = (
                f"{station.address}, "
                f"{station.city}, "
                f"{station.state}"
            )

            try:

                result = geocode_address(address)

                if result:

                    station.latitude = result["latitude"]
                    station.longitude = result["longitude"]
                    station.geocoded = True

                    station.save(
                        update_fields=[
                            "latitude",
                            "longitude",
                            "geocoded",
                        ]
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"[{index}/{total}] "
                            f"Geocoded: {station.name}"
                        )
                    )

                else:

                    self.stdout.write(
                        self.style.WARNING(
                            f"[{index}/{total}] "
                            f"No match: {station.name}"
                        )
                    )

            except Exception as exc:

                self.stderr.write(
                    f"[{index}/{total}] "
                    f"Failed: {station.id}: {exc}"
                )

            time.sleep(0.2)