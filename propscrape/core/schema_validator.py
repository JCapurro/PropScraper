"""
MongoDB Schema Validator for PropScrape Data Lake
Provides JSON Schema validation for listings collection
"""

from typing import Dict, Any

# JSON Schema for listings_current collection
LISTINGS_SCHEMA = {
    "bsonType": "object",
    "required": ["platform", "platform_listing_id", "operation_type", "property_type", "currency", "status"],
    "properties": {
        "platform": {
            "bsonType": "string",
            "enum": ["zonaprop", "mercadolibre", "properati", "argenprop"],
            "description": "Source platform identifier"
        },
        "platform_listing_id": {
            "bsonType": "string",
            "description": "Unique identifier from the source platform"
        },
        "listing_url": {
            "bsonType": "string",
            "description": "URL to the listing on the source platform"
        },
        "operation_type": {
            "bsonType": "string",
            "enum": ["sale", "rent"],
            "description": "Type of real estate operation"
        },
        "property_type": {
            "bsonType": "string",
            "description": "Type of property (apartment, house, etc.)"
        },
        "price": {
            "bsonType": ["double", "null"],
            "minimum": 0,
            "description": "Listing price (must be non-negative)"
        },
        "currency": {
            "bsonType": "string",
            "enum": ["ARS", "USD", "EUR"],
            "description": "Currency code"
        },
        "expenses": {
            "bsonType": ["double", "null"],
            "minimum": 0,
            "description": "Monthly expenses/expensas"
        },
        "address_text": {
            "bsonType": ["string", "null"],
            "description": "Text address of the property"
        },
        "geo_lat": {
            "bsonType": ["double", "null"],
            "minimum": -90,
            "maximum": 90,
            "description": "Latitude coordinate"
        },
        "geo_lng": {
            "bsonType": ["double", "null"],
            "minimum": -180,
            "maximum": 180,
            "description": "Longitude coordinate"
        },
        "geo_location": {
            "bsonType": ["object", "null"],
            "description": "GeoJSON Point for geospatial queries",
            "properties": {
                "type": {
                    "bsonType": "string",
                    "enum": ["Point"]
                },
                "coordinates": {
                    "bsonType": "array",
                    "minItems": 2,
                    "maxItems": 2,
                    "items": {
                        "bsonType": "double"
                    }
                }
            }
        },
        "surface_total": {
            "bsonType": ["double", "null"],
            "minimum": 0,
            "description": "Total surface area in square meters"
        },
        "surface_covered": {
            "bsonType": ["double", "null"],
            "minimum": 0,
            "description": "Covered surface area in square meters"
        },
        "rooms": {
            "bsonType": ["int", "null"],
            "minimum": 0,
            "description": "Number of rooms/ambientes"
        },
        "bedrooms": {
            "bsonType": ["int", "null"],
            "minimum": 0,
            "description": "Number of bedrooms"
        },
        "bathrooms": {
            "bsonType": ["int", "null"],
            "minimum": 0,
            "description": "Number of bathrooms"
        },
        "title": {
            "bsonType": ["string", "null"],
            "description": "Listing title"
        },
        "description": {
            "bsonType": ["string", "null"],
            "description": "Listing description"
        },
        "images": {
            "bsonType": "array",
            "items": {
                "bsonType": "string"
            },
            "description": "Array of image URLs"
        },
        "agent_publisher": {
            "bsonType": ["string", "null"],
            "description": "Name of real estate agent or publisher"
        },
        "status": {
            "bsonType": "string",
            "enum": ["active", "delisted", "paused", "sold", "rented"],
            "description": "Current status of the listing"
        },
        "source_created_at": {
            "bsonType": ["date", "null"],
            "description": "Creation date on source platform"
        },
        "source_updated_at": {
            "bsonType": ["date", "null"],
            "description": "Last update date on source platform"
        },
        "ingested_at": {
            "bsonType": "date",
            "description": "Timestamp when ingested into data lake"
        }
    }
}

# Schema for ingestion_runs collection
INGESTION_RUNS_SCHEMA = {
    "bsonType": "object",
    "required": ["timestamp", "platform", "status"],
    "properties": {
        "timestamp": {
            "bsonType": "date",
            "description": "Run timestamp"
        },
        "platform": {
            "bsonType": "string",
            "description": "Platform that was scraped"
        },
        "listings_processed": {
            "bsonType": "int",
            "minimum": 0,
            "description": "Number of listings processed"
        },
        "listings_new": {
            "bsonType": "int",
            "minimum": 0,
            "description": "Number of new listings inserted"
        },
        "listings_updated": {
            "bsonType": "int",
            "minimum": 0,
            "description": "Number of listings updated"
        },
        "errors": {
            "bsonType": "int",
            "minimum": 0,
            "description": "Number of errors encountered"
        },
        "status": {
            "bsonType": "string",
            "enum": ["started", "completed", "failed"],
            "description": "Run status"
        }
    }
}


def apply_schema_validation(db) -> Dict[str, Any]:
    """
    Apply JSON Schema validation to MongoDB collections
    
    Args:
        db: MongoDB database instance
        
    Returns:
        Dictionary with results for each collection
    """
    results = {}
    
    # Apply validation to DataLake
    try:
        db.command({
            "collMod": "DataLake",
            "validator": {"$jsonSchema": LISTINGS_SCHEMA},
            "validationLevel": "moderate",  # moderate = existing docs exempt
            "validationAction": "error"      # error = reject invalid inserts
        })
        results["DataLake"] = "✓ Schema validation applied"
    except Exception as e:
        results["DataLake"] = f"✗ Error: {e}"
    
    # Apply validation to ingestion_runs
    try:
        db.command({
            "collMod": "ingestion_runs",
            "validator": {"$jsonSchema": INGESTION_RUNS_SCHEMA},
            "validationLevel": "moderate",
            "validationAction": "error"
        })
        results["ingestion_runs"] = "✓ Schema validation applied"
    except Exception as e:
        results["ingestion_runs"] = f"✗ Error: {e}"
    
    return results


def get_validation_info(db) -> Dict[str, Any]:
    """
    Get current validation rules for collections
    
    Args:
        db: MongoDB database instance
        
    Returns:
        Dictionary with validation info for each collection
    """
    info = {}
    
    for collection_name in ["DataLake", "ingestion_runs"]:
        try:
            collection_info = db.command({"listCollections": 1, "filter": {"name": collection_name}})
            if collection_info["cursor"]["firstBatch"]:
                options = collection_info["cursor"]["firstBatch"][0].get("options", {})
                info[collection_name] = {
                    "validator": options.get("validator", "No validator"),
                    "validationLevel": options.get("validationLevel", "N/A"),
                    "validationAction": options.get("validationAction", "N/A")
                }
            else:
                info[collection_name] = "Collection not found"
        except Exception as e:
            info[collection_name] = f"Error: {e}"
    
    return info
