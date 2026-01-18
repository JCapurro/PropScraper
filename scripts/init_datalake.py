"""
Data Lake Initialization Script
Initializes the PropScrape data lake with proper indexes and schema validation
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from propscrape.core.config import settings
from propscrape.core.schema_validator import apply_schema_validation, get_validation_info
from pprint import pprint


def main():
    """Initialize the data lake"""
    
    print("\n" + "=" * 80)
    print("PropScrape Data Lake Initialization".center(80))
    print("=" * 80 + "\n")
    
    # Connect to MongoDB
    print("1. Connecting to MongoDB...")
    try:
        client = MongoClient(settings.DATABASE_URL, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print(f"   ✓ Connected to: {settings.DATABASE_URL}\n")
    except ServerSelectionTimeoutError:
        print(f"   ✗ ERROR: Could not connect to {settings.DATABASE_URL}")
        print("   Make sure MongoDB is running (mongod)")
        return 1
    
    db = client["RealStates"]
    
    # Create collections if they don't exist
    print("2. Ensuring collections exist...")
    existing_collections = db.list_collection_names()
    
    if "DataLake" not in existing_collections:
        db.create_collection("DataLake")
        print("   ✓ Created: DataLake")
    else:
        print("   ✓ Exists: DataLake")
    
    if "ingestion_runs" not in existing_collections:
        db.create_collection("ingestion_runs")
        print("   ✓ Created: ingestion_runs")
    else:
        print("   ✓ Exists: ingestion_runs")
    
    print()
    
    # Apply schema validation
    print("3. Applying JSON Schema validation...")
    validation_results = apply_schema_validation(db)
    for collection, result in validation_results.items():
        print(f"   {result}")
    print()
    
    # Create indexes
    print("4. Creating optimized indexes...")
    print("   (This may take a few moments)\n")
    
    listings_collection = db["DataLake"]
    ingestion_runs_collection = db["ingestion_runs"]
    
    # Drop existing indexes (except _id)
    print("   Dropping old indexes (except _id)...")
    try:
        listings_collection.drop_indexes()
        ingestion_runs_collection.drop_indexes()
        print("   ✓ Old indexes dropped\n")
    except Exception as e:
        print(f"   ⚠ Could not drop indexes: {e}\n")
    
    # Create new indexes using the optimized create_indexes function
    # We'll import and call it directly
    from propscrape.core.mongo_db import create_indexes
    try:
        create_indexes()
        print()
    except Exception as e:
        print(f"   ✗ Error creating indexes: {e}\n")
    
    # Verify indexes
    print("5. Verifying indexes...")
    
    listings_indexes = list(listings_collection.list_indexes())
    print(f"\n   listings_current ({len(listings_indexes)} indexes):")
    for idx in listings_indexes:
        name = idx.get('name', 'unknown')
        keys = idx.get('key', {})
        unique = " [UNIQUE]" if idx.get('unique', False) else ""
        print(f"     - {name}: {dict(keys)}{unique}")
    
    ingestion_indexes = list(ingestion_runs_collection.list_indexes())
    print(f"\n   ingestion_runs ({len(ingestion_indexes)} indexes):")
    for idx in ingestion_indexes:
        name = idx.get('name', 'unknown')
        keys = idx.get('key', {})
        print(f"     - {name}: {dict(keys)}")
    
    print()
    
    # Show validation rules
    print("6. Verification - Schema Validation Rules...")
    validation_info = get_validation_info(db)
    for collection, info in validation_info.items():
        print(f"\n   {collection}:")
        if isinstance(info, dict):
            print(f"     Validation Level: {info.get('validationLevel', 'N/A')}")
            print(f"     Validation Action: {info.get('validationAction', 'N/A')}")
            validator = info.get('validator')
            if validator != "No validator":
                print(f"     Validator: Active (JSON Schema)")
            else:
                print(f"     Validator: None")
        else:
            print(f"     {info}")
    
    # Statistics
    print("\n" + "=" * 80)
    print("7. Current Database Statistics...")
    stats = db.command("dbStats")
    
    print(f"\n   Database: {stats.get('db')}")
    print(f"   Collections: {stats.get('collections')}")
    print(f"   Total Size: {stats.get('dataSize', 0) / 1024 / 1024:.2f} MB")
    print(f"   Index Size: {stats.get('indexSize', 0) / 1024 / 1024:.2f} MB")
    
    # Collection counts
    listings_count = listings_collection.count_documents({})
    runs_count = ingestion_runs_collection.count_documents({})
    
    print(f"\n   Listings: {listings_count:,}")
    print(f"   Ingestion Runs: {runs_count}")
    
    if listings_count > 0:
        # Platform breakdown
        pipeline = [{"$group": {"_id": "$platform", "count": {"$sum": 1}}}]
        platform_counts = list(listings_collection.aggregate(pipeline))
        
        print("\n   Platform Breakdown:")
        for item in platform_counts:
            print(f"     - {item['_id']}: {item['count']:,}")
    
    # Final message
    print("\n" + "=" * 80)
    print("✓ DATA LAKE INITIALIZATION COMPLETE")
    print("=" * 80)
    
    print("\nYour data lake is ready for:")
    print("  • Cross-platform queries")
    print("  • Geospatial searches")
    print("  • Full-text search")
    print("  • Data validation")
    
    print("\nNext steps:")
    print("  • Run ingestion: python -m propscrape.services.ingestion")
    print("  • Query examples: python scripts/query_examples.py")
    print("  • Data quality: python scripts/data_quality_check.py")
    
    print("\nMongoDB Compass connection:")
    print(f"  {settings.DATABASE_URL}")
    print()
    
    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
