import time
import cloudscraper
from typing import Generator, Optional, Dict, List, Any
from datetime import datetime, timezone
from ..core.models import UnifiedListing
from ..core.zones_config import ZONES_CONFIG, OPERATION_TYPES
from .base import BaseConnector


class ZonapropConnector(BaseConnector):
    def __init__(self):
        super().__init__("zonaprop")
        self.current_page = 1
        self.total_pages = 0
        self.total_listings = 0
        self.listings_per_page = 30  # API máximo es 30, no acepta valores mayores
        self.pagination_info = {}
        # Create cloudscraper session that handles Cloudflare
        self.session = cloudscraper.create_scraper()

    def authenticate(self):
        """Mock authentication with Cloudflare clearance"""
        time.sleep(0.5)
        print(f"[{self.platform_name}] Authenticated (Mock)")

    def get_property(self, page: int = 1, offset: int = 0, limit: int = 30, 
                     province_code: str = "6", operation_code: str = "1", 
                     zone_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch properties from Zonaprop API with pagination and zone/operation filters
        
        Args:
            page: Page number to fetch (1-indexed)
            offset: Starting position for results
            limit: Number of results per page (API máximo: 30)
            province_code: Province code (default: "6" for Buenos Aires)
            operation_code: Operation type code ("1" for sale, "2" for rent)
            zone_code: Zone code within province (optional)
        
        Returns:
            API response JSON or None if error occurs
        """
        url = "https://www.zonaprop.com.ar/rplis-api/postings?dynamicListingSearch=true"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
            "Accept": "*/*",
            "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://www.zonaprop.com.ar/inmuebles-venta-capital-federal.html",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.zonaprop.com.ar",
            "Alt-Used": "www.zonaprop.com.ar",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=4",
            "TE": "trailers",
        }
        
        payload = {
            "q": None,
            "direccion": None,
            "moneda": "",
            "preciomin": None,
            "preciomax": None,
            "services": "",
            "general": "",
            "searchbykeyword": "",
            "amenidades": "",
            "caracteristicasprop": None,
            "comodidades": "",
            "disposicion": None,
            "roomType": "",
            "outside": "",
            "areaPrivativa": "",
            "areaComun": "",
            "multipleRets": "",
            "tipoDePropiedad": "2",
            "subtipoDePropiedad": None,
            "tipoDeOperacion": operation_code,
            "garages": None,
            "antiguedad": None,
            "expensasminimo": None,
            "expensasmaximo": None,
            "withoutguarantor": None,
            "habitacionesminimo": 0,
            "habitacionesmaximo": 0,
            "ambientesminimo": 0,
            "ambientesmaximo": 0,
            "banos": None,
            "superficieCubierta": 1,
            "idunidaddemedida": 1,
            "metroscuadradomin": None,
            "metroscuadradomax": None,
            "tipoAnunciante": "ALL",
            "grupoTipoDeMultimedia": "",
            "publicacion": None,
            "sort": "relevance",
            "etapaDeDesarrollo": "",
            "auctions": None,
            "polygonApplied": None,
            "idInmobiliaria": None,
            "excludePostingContacted": "",
            "banks": "",
            "places": "",
            "condominio": "",
            "preTipoDeOperacion": operation_code,
            "city": None,
            "province": province_code,
            "zone": zone_code,
            "valueZone": None,
            "subZone": None,
            "coordenates": None,
            "page": page,
            "offset": offset,
            "limit": limit
        }
        
        try:
            response = self.session.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            # Ensure proper encoding
            response.encoding = 'utf-8'
            data = response.json()
            
            # Extract and store pagination info
            if "paging" in data:
                self.pagination_info = data["paging"]
                self.total_pages = data["paging"].get("totalPages", 0)
                self.total_listings = data["paging"].get("total", 0)
                self.current_page = data["paging"].get("currentPage", page)
            
            return data
            
        except Exception as e:
            print(f"[{self.platform_name}] Error fetching properties: {e}")
            return None

    def has_next_page(self) -> bool:
        """Check if there are more pages to fetch"""
        return not self.pagination_info.get("lastPage", True)

    def get_next_page_offset(self) -> int:
        """Calculate offset for next page"""
        return self.pagination_info.get("offset", 0) + self.pagination_info.get("limit", 30)

    def fetch_listings_for_zone(self, zone_key: str, operation_key: str, 
                                max_pages: Optional[int] = None) -> Generator[UnifiedListing, None, None]:
        """
        Fetch listings for a specific zone and operation type
        
        Args:
            zone_key: Zone identifier (e.g., 'capital_federal', 'zona_norte_gba')
            operation_key: Operation type ('sale' or 'rent')
            max_pages: Maximum number of pages to fetch (None = fetch all)
        
        Yields:
            UnifiedListing objects
        """
        # Get zone and operation config
        if zone_key not in ZONES_CONFIG:
            print(f"[{self.platform_name}] Zone '{zone_key}' not found in configuration")
            return
        
        if operation_key not in OPERATION_TYPES:
            print(f"[{self.platform_name}] Operation '{operation_key}' not found in configuration")
            return
        
        zone_config = ZONES_CONFIG[zone_key]
        operation_config = OPERATION_TYPES[operation_key]
        
        province_code = zone_config["province_code"]
        operation_code = operation_config["code"]
        zone_code = zone_config["zone_code"]
        
        print(f"[{self.platform_name}] Starting scrape: {zone_config['display_name']} - {operation_config['display_name']}")
        
        # Use fetch_listings with proper parameters
        yield from self.fetch_listings(
            province_code=province_code,
            operation_code=operation_code,
            zone_code=zone_code,
            max_pages=max_pages
        )
    
    def fetch_listings_multi_zone(self, zones_list: List[str], operations_list: List[str],
                                  max_pages_per_zone: Optional[int] = None) -> Generator[UnifiedListing, None, None]:
        """
        Fetch listings for multiple zones and operation types
        
        Args:
            zones_list: List of zone keys (e.g., ['capital_federal', 'zona_norte_gba'])
            operations_list: List of operation keys (e.g., ['sale', 'rent'])
            max_pages_per_zone: Maximum pages per zone
        
        Yields:
            UnifiedListing objects from all zones and operations
        """
        total_zones = len(zones_list) * len(operations_list)
        current = 0
        
        for zone_key in zones_list:
            for operation_key in operations_list:
                current += 1
                zone_config = ZONES_CONFIG.get(zone_key)
                operation_config = OPERATION_TYPES.get(operation_key)
                
                if not zone_config or not operation_config:
                    continue
                
                print(f"\n[{self.platform_name}] [{current}/{total_zones}] Processing: {zone_config['display_name']} - {operation_config['display_name']}")
                
                # Yield listings for this zone/operation combination
                for listing in self.fetch_listings_for_zone(zone_key, operation_key, max_pages_per_zone):
                    yield listing
                
                # Add delay between zone requests to be respectful
                time.sleep(2)

    def fetch_listings(self, max_pages: Optional[int] = None, province_code: str = "6", 
                      operation_code: str = "1", zone_code: Optional[str] = None) -> Generator[UnifiedListing, None, None]:
        """
        Fetch and yield listings from Zonaprop API with pagination support
        
        Args:
            max_pages: Maximum number of pages to fetch (None = fetch all)
            province_code: Province code to filter by
            operation_code: Operation type code to filter by
            zone_code: Zone code to filter by (optional)
        
        Yields:
            UnifiedListing objects
        """
        page = 1
        pages_fetched = 0
        
        while True:
            # Respect max_pages limit
            if max_pages and pages_fetched >= max_pages:
                break
            
            print(f"[{self.platform_name}] Fetching page {page}...")
            
            # Calculate offset for pagination
            offset = (page - 1) * self.listings_per_page
            
            # Fetch data for current page
            data = self.get_property(page=page, limit=self.listings_per_page, offset=offset,
                                    province_code=province_code, operation_code=operation_code,
                                    zone_code=zone_code)
            
            if not data or "listPostings" not in data:
                print(f"[{self.platform_name}] No data received or invalid response format")
                break
            
            postings = data.get("listPostings", [])
            
            if not postings:
                print(f"[{self.platform_name}] No postings found on page {page}")
                break
            
            # Transform each posting to UnifiedListing
            for posting in postings:
                try:
                    # 1. Basic IDs
                    listing_id = posting.get("postingId") or posting.get("id") or ""
                    listing_id = str(listing_id) if listing_id else ""

                    if not listing_id:
                        continue
                    
                    # 2. URLs
                    url_path = posting.get("url", "")
                    listing_url = f"https://www.zonaprop.com.ar{url_path}" if url_path.startswith("/") else url_path
                    
                    # 3. Titles and Descriptions
                    title = posting.get("title", "")
                    description = posting.get("descriptionNormalized") or posting.get("description", "")
                    
                    # 4. Operations and Prices
                    op_types = posting.get("priceOperationTypes", [])
                    operation_type = "sale"  # Default
                    price = 0.0
                    currency = "USD"
                    
                    if op_types and len(op_types) > 0:
                        op_data = op_types[0]
                        op_name = op_data.get("operationType", {}).get("name", "Venta").lower()
                        if "alquiler" in op_name:
                            operation_type = "rent"
                        
                        prices = op_data.get("prices", [])
                        if prices:
                            price = float(prices[0].get("amount", 0))
                            currency = prices[0].get("currency", "USD")

                    # 5. Expenses
                    expenses_data = posting.get("expenses", {})
                    expenses = None
                    if expenses_data and isinstance(expenses_data, dict):
                        exp_amount = expenses_data.get("amount")
                        if exp_amount:
                            expenses = float(exp_amount)
                        
                    # 6. Location
                    location_data = posting.get("postingLocation", {})
                    address_data = location_data.get("address", {})
                    address_text = address_data.get("name", "")
                    
                    geo_data = location_data.get("postingGeolocation", {}).get("geolocation", {})
                    geo_lat = geo_data.get("latitude")
                    geo_lng = geo_data.get("longitude")
                    
                    # 7. Features (Surface, Rooms, etc.)
                    main_features = posting.get("mainFeatures", {})
                    
                    def get_feature_value(key):
                        feat = main_features.get(key, {})
                        val = feat.get("value")
                        if val and str(val).replace(".", "").isdigit():
                            return float(val)
                        return None

                    # Zonaprop keys: CFT100=Total, CFT101=Covered, CFT1=Ambientes, CFT2=Dormitorios, CFT3=Baños
                    surface_total = get_feature_value("CFT100")
                    surface_covered = get_feature_value("CFT101")
                    rooms = int(get_feature_value("CFT1")) if get_feature_value("CFT1") else None
                    bedrooms = int(get_feature_value("CFT2")) if get_feature_value("CFT2") else None
                    bathrooms = int(get_feature_value("CFT3")) if get_feature_value("CFT3") else None

                    # 8. Images
                    visible_pics = posting.get("visiblePictures", {}).get("pictures", [])
                    images = []
                    for pic in visible_pics:
                        url = pic.get("url730x532") or pic.get("url360x266")
                        if url:
                            images.append(url)
                            
                    # 9. Publisher
                    publisher = posting.get("publisher", {})
                    agent = publisher.get("name") if publisher else None
                    
                    # 10. Property Type
                    prop_type_data = posting.get("realEstateType", {})
                    property_type = prop_type_data.get("name", "unknown") if prop_type_data else "unknown"
                    
                    # 11. Timestamps
                    source_created_at = datetime.now(timezone.utc)
                    source_updated_at = None
                    modified_date_str = posting.get("modified_date")
                    if modified_date_str:
                        try:
                            # Format: 2026-01-20T11:49:39-0500
                            source_updated_at = datetime.fromisoformat(modified_date_str.replace("-0500", "-05:00").replace("-0300", "-03:00"))
                        except (ValueError, AttributeError):
                            pass

                    # Validate coordinates
                    if (geo_lat is None) != (geo_lng is None):
                        geo_lat = None
                        geo_lng = None
                    
                    # Create UnifiedListing object
                    listing = UnifiedListing(
                        platform=self.platform_name,
                        platform_listing_id=listing_id,
                        listing_url=listing_url,
                        operation_type=operation_type,
                        property_type=property_type,
                        currency=currency,
                        price=price,
                        expenses=expenses,
                        status="active",
                        address_text=address_text,
                        geo_lat=geo_lat,
                        geo_lng=geo_lng,
                        surface_total=surface_total,
                        surface_covered=surface_covered,
                        rooms=rooms,
                        bedrooms=bedrooms,
                        bathrooms=bathrooms,
                        title=title,
                        description=description,
                        images=images,
                        agent_publisher=agent,
                        source_created_at=source_created_at,
                        source_updated_at=source_updated_at
                    )
                    
                    yield listing
                    
                except Exception as e:
                    print(f"[{self.platform_name}] Error transforming posting {listing_id}: {e}")
                    continue
            
            # Check if there are more pages
            if not self.has_next_page():
                print(f"[{self.platform_name}] Reached last page")
                break
            
            page += 1
            pages_fetched += 1
            
            # Add delay between requests to be respectful (reduced from 1s to 0.5s)
            time.sleep(0.5)
