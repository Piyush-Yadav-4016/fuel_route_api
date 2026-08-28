import csv

from django.core.management.base import BaseCommand

from routing.models import FuelStation


class Command(BaseCommand):
    help = "Import fuel prices from CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="data/fuel_prices.csv"
        )

    def handle(self, *args, **options):

        file_path = options["file"]

        FuelStation.objects.all().delete()

        with open(file_path, "r", encoding="utf-8-sig") as file:

            reader = csv.DictReader(file)

            stations = []

            for row in reader:

                stations.append(
                    FuelStation(
                        name=row["Truckstop Name"],
                        address=row.get("Address", ""),
                        city=row.get("City", ""),
                        state=row.get("State", ""),
                        price=float(row["Retail Price"]),
                    )
                )

        FuelStation.objects.bulk_create(
            stations,
            batch_size=1000
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(stations)} stations"
            )
        )