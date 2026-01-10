import time
import random
from typing import Generator
from datetime import datetime
from ..core.models import UnifiedListing
from .base import BaseConnector

class ZonapropConnector(BaseConnector):
    def __init__(self):
        super().__init__("zonaprop")

    def authenticate(self):
        # Mock auth
        time.sleep(0.5)
        print(f"[{self.platform_name}] Authenticated (Mock)")

    def fetch_listings(self) -> Generator[UnifiedListing, None, None]:
        print(f"[{self.platform_name}] Fetching {limit} listings...")

        #Create here the logic to request to api
        for i in range(limit):
            listing_id = f"ZPROP-{random.randint(100000, 999999)}"
            price = random.randint(50000, 500000)
            
            yield UnifiedListing(
                platform=self.platform_name,
                platform_listing_id=listing_id,
                listing_url=f"https://www.zonaprop.com.ar/propiedades/{listing_id}.html",
                operation_type=random.choice(["sale", "rent"]),
                property_type=random.choice(["apartment", "house"]),
                price=float(price),
                currency="USD",
                address_text=f"Av. Mock {random.randint(1, 5000)}",
                geo_lat=-34.6037 + (random.random() - 0.5) * 0.1,
                geo_lng=-58.3816 + (random.random() - 0.5) * 0.1,
                surface_total=random.randint(40, 200),
                rooms=random.randint(1, 5),
                status="active",
                source_created_at=datetime.utcnow(),
                source_updated_at=datetime.utcnow(),
                title=f"Beautiful mock property {i+1}",
                description="This is a generated mock listing for testing purposes."
            )
