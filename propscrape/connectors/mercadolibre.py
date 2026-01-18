import time
import random
from typing import Generator
from datetime import datetime, timezone
from ..core.models import UnifiedListing
from .base import BaseConnector

class MercadoLibreConnector(BaseConnector):
    def __init__(self):
        super().__init__("mercadolibre")

    def authenticate(self):
        # Mock auth
        time.sleep(0.5)
        print(f"[{self.platform_name}] Authenticated (Mock)")

    def fetch_listings(self) -> Generator[UnifiedListing, None, None]:
        print(f"[{self.platform_name}] Fetching {limit} listings...")
        for i in range(limit):
            listing_id = f"MLA-{random.randint(100000, 999999)}"
            price = random.randint(10000000, 50000000) # ARS usually
            
            yield UnifiedListing(
                platform=self.platform_name,
                platform_listing_id=listing_id,
                listing_url=f"https://house.mercadolibre.com.ar/{listing_id}",
                operation_type=random.choice(["sale", "rent"]),
                property_type=random.choice(["apartment", "house", "ph"]),
                price=float(price),
                currency="ARS",
                address_text=f"Calle Falsa {random.randint(123, 999)}",
                geo_lat=-34.6037 + (random.random() - 0.5) * 0.1,
                geo_lng=-58.3816 + (random.random() - 0.5) * 0.1,
                surface_total=random.randint(30, 150),
                rooms=random.randint(1, 4),
                status="active",
                source_created_at=datetime.now(timezone.utc),
                source_updated_at=datetime.now(timezone.utc),
                title=f"Meli Mock Prop {i+1}",
                description="Another mock listing from MercadoLibre."
            )
