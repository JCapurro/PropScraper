"""
MongoDB connection and utilities for PropScrape
"""

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from .config import settings

# Parse MongoDB connection string
try:
    client = MongoClient(settings.DATABASE_URL, serverSelectionTimeoutMS=5000)
    # Verify connection
    client.admin.command('ping')
    print(f"[MongoDB] Connected to: {settings.DATABASE_URL}")
except ServerSelectionTimeoutError:
    print(f"[MongoDB] ERROR: Could not connect to {settings.DATABASE_URL}")
    print("[MongoDB] Make sure MongoDB is running. You can start it with:")
    print("  mongod")
    print("Or use MongoDB Atlas cloud at: https://www.mongodb.com/cloud/atlas")
    raise

db = client["RealStates"]

# Collections
listings_collection = db["DataLake"]
ingestion_runs_collection = db["ingestion_runs"]

# Create indexes for better query performance
def create_indexes():
    """Create optimized indexes for data lake queries"""
    
    print("[MongoDB] Creating indexes for data lake...")
    
    # === BASIC INDEXES ===
    
    # Platform (for filtering by source)
    listings_collection.create_index("platform")
    print("  ✓ Index: platform")
    
    # Platform listing ID (for lookups)
    listings_collection.create_index("platform_listing_id")
    print("  ✓ Index: platform_listing_id")
    
    # Composite unique index (prevents duplicates)
    listings_collection.create_index(
        [("platform", 1), ("platform_listing_id", 1)],
        unique=True,
        name="unique_platform_listing"
    )
    print("  ✓ Index: (platform, platform_listing_id) [UNIQUE]")
    
    # === QUERY OPTIMIZATION INDEXES ===
    
    # Operation type (sale/rent filtering)
    listings_collection.create_index("operation_type")
    print("  ✓ Index: operation_type")
    
    # Status (active/delisted filtering)
    listings_collection.create_index("status")
    print("  ✓ Index: status")
    
    # Composite for common searches (operation + property type + price)
    listings_collection.create_index([
        ("operation_type", 1),
        ("property_type", 1),
        ("price", 1)
    ], name="search_operation_property_price")
    print("  ✓ Index: (operation_type, property_type, price)")
    
    # === TEMPORAL INDEXES ===
    
    # Source created date (for temporal analysis)
    listings_collection.create_index("source_created_at")
    print("  ✓ Index: source_created_at")
    
    # Ingested date descending (for "latest" queries)
    listings_collection.create_index([("ingested_at", -1)], name="ingested_at_desc")
    print("  ✓ Index: ingested_at (descending)")
    
    # === GEOSPATIAL INDEX ===
    
    # 2dsphere index for location-based queries
    # This allows queries like "properties within 2km of a point"
    try:
        listings_collection.create_index([("geo_location", "2dsphere")], name="geo_location_2dsphere")
        print("  ✓ Index: geo_location (2dsphere) - for geospatial queries")
    except Exception as e:
        print(f"  ⚠ Geospatial index not created (field may not exist yet): {e}")
    
    # === TEXT SEARCH INDEX ===
    
    # Text index for full-text search in title and description
    try:
        listings_collection.create_index([
            ("title", "text"),
            ("description", "text")
        ], name="text_search_title_description", default_language="spanish")
        print("  ✓ Index: (title, description) [TEXT] - for full-text search")
    except Exception as e:
        print(f"  ⚠ Text index may already exist: {e}")
    
    # === INGESTION RUNS INDEXES ===
    
    ingestion_runs_collection.create_index("timestamp")
    print("  ✓ Index: ingestion_runs.timestamp")
    
    ingestion_runs_collection.create_index("platform")
    print("  ✓ Index: ingestion_runs.platform")
    
    ingestion_runs_collection.create_index([("platform", 1), ("timestamp", -1)], name="platform_timestamp_desc")
    print("  ✓ Index: ingestion_runs.(platform, timestamp)")
    
    print("[MongoDB] ✓ All indexes created successfully")

# Create indexes on startup
try:
    create_indexes()
except Exception as e:
    print(f"[MongoDB] Warning: Could not create indexes: {e}")

def close_connection():
    """Close MongoDB connection"""
    client.close()
    print("[MongoDB] Connection closed")
