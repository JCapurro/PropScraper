"""
Configuration for Argentine zones/provinces and their codes for Zonaprop API
"""

ZONES_CONFIG = {
    "capital_federal": {
        "display_name": "Capital Federal",
        "province_code": "6",
        "zone_code": None,
        "description": "Ciudad Autónoma de Buenos Aires"
    },
    "zona_norte_gba": {
        "display_name": "Zona Norte GBA",
        "province_code": "990",
        "zone_code": None,
        "description": "Zona Norte del Gran Buenos Aires"
    },
    "santa_fe": {
        "display_name": "Santa Fe",
        "province_code": "25",
        "zone_code": None,
        "description": "Provincia de Santa Fe"
    },
    "cordoba": {
        "display_name": "Córdoba",
        "province_code": "7",
        "zone_code": None,
        "description": "Provincia de Córdoba"
    },
    "mendoza": {
        "display_name": "Mendoza",
        "province_code": "17",
        "zone_code": None,
        "description": "Provincia de Mendoza"
    },
    "entre_rios": {
        "display_name": "Entre Ríos",
        "province_code": "12",
        "zone_code": None,
        "description": "Provincia de Entre Ríos"
    }
}

OPERATION_TYPES = {
    "sale": {
        "code": "1",
        "display_name": "Venta"
    },
    "rent": {
        "code": "2",
        "display_name": "Alquiler"
    }
}

PROPERTY_TYPES = {
    "apartment": "1",
    "house": "2",
    "land": "3",
    "commercial": "4",
    "all": ""
}

# All zones to scrape
ZONES_TO_SCRAPE = list(ZONES_CONFIG.keys())

# All operation types to scrape
OPERATIONS_TO_SCRAPE = list(OPERATION_TYPES.keys())
