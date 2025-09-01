import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.cache import cache
from properties.models import Property

from properties.signals import ALL_PROPERTIES_KEY

ADJECTIVES = [
    "Cozy", "Spacious", "Modern", "Charming", "Elegant", "Sunny", "Quiet", "Renovated",
    "Premium", "Affordable", "Luxurious", "Stylish", "Comfortable", "Bright"
]

TYPES = [
    "Apartment", "Studio", "Condo", "Loft", "Townhouse", "Bungalow", "Villa", "Cottage",
    "Duplex", "Penthouse"
]

CITIES = [
    "Accra", "Kumasi", "Tema", "Takoradi", "Cape Coast", "Tamale", "Ho", "Koforidua",
    "Sunyani", "Bolgatanga"
]

DESCRIPTIONS = [
    "Close to shops and public transport.",
    "Great neighborhood with parks nearby.",
    "Recently renovated with modern finishes.",
    "Perfect for families and professionals.",
    "Offers stunning city views.",
    "Walking distance to schools and markets.",
    "Secure compound with parking.",
    "Includes fitted kitchen and wardrobes.",
]


class Command(BaseCommand):
    help = "Seed the database with Property rows."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=20,
                            help="Number of properties to create")
        parser.add_argument("--flush", action="store_true",
                            help="Delete all Property rows before seeding")

    def handle(self, *args, **options):
        count = options["count"]
        if options["flush"]:
            deleted, _ = Property.objects.all().delete()
            self.stdout.write(self.style.WARNING(
                f"Flushed {deleted} existing Property rows."))

        created = 0
        for i in range(count):
            city = random.choice(CITIES)
            title = f"{random.choice(ADJECTIVES)} {random.choice(TYPES)} in {city} #{random.randint(1000, 9999)}"
            description = random.choice(DESCRIPTIONS)

            # Generate a price with two decimal places between 30,000 and 1,000,000
            price_whole = random.randint(30_000, 1_000_000)
            price_cents = random.randint(0, 99)
            price = Decimal(price_whole) + \
                (Decimal(price_cents) / Decimal("100"))

            Property.objects.create(
                title=title,
                description=description,
                price=price,
                location=city,
            )
            created += 1

        # Clear list cache explicitly (in addition to signals) to be safe
        cache.delete(ALL_PROPERTIES_KEY)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {created} Property rows."))
