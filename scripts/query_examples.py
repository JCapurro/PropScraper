"""
Query Examples for PropScrape Data Lake
Demonstrates powerful cross-platform queries
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from propscrape.core.config import settings
from pprint import pprint
from datetime import datetime, timedelta


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


def query_1_top_cheapest_cross_platform(collection):
    """Find the 10 cheapest properties across ALL platforms"""
    print_section("QUERY 1: Top 10 Cheapest Properties (Cross-Platform)")
    
    cursor = collection.find({
        "operation_type": "sale",
        "price": {"$ne": None, "$gt": 0}
    }).sort("price", 1).limit(10)
    
    print("Listing ID, Platform, Price, Title")
    print("-" * 80)
    
    for i, doc in enumerate(cursor, 1):
        title = doc.get('title', 'N/A')[:40] if doc.get('title') else 'N/A'
        price = doc.get('price', 0)
        currency = doc.get('currency', 'N/A')
        platform = doc.get('platform', 'N/A')
        
        print(f"{i}. [{platform.upper()}] ${price:,.0f} {currency} - {title}")


def query_2_detect_duplicates(collection):
    """Detect potential duplicate properties across platforms"""
    print_section("QUERY 2: Detect Duplicates Across Platforms")
    
    pipeline = [
        # Match only properties with coordinates
        {"$match": {
            "geo_lat": {"$ne": None},
            "geo_lng": {"$ne": None},
            "rooms": {"$ne": None}
        }},
        # Group by approximate location and characteristics
        {"$group": {
            "_id": {
                "lat_rounded": {"$round": ["$geo_lat", 3]},  # ~110m precision
                "lng_rounded": {"$round": ["$geo_lng", 3]},
                "rooms": "$rooms",
                "operation_type": "$operation_type"
            },
            "platforms": {"$addToSet": "$platform"},
            "listings": {"$push": {
                "platform": "$platform",
                "title": "$title",
                "price": "$price",
                "currency": "$currency",
                "url": "$listing_url"
            }},
            "count": {"$sum": 1}
        }},
        # Filter: only groups with multiple platforms
        {"$match": {
            "count": {"$gt": 1},
            "platforms.1": {"$exists": True}  # At least 2 different platforms
        }},
        {"$limit": 5}
    ]
    
    results = list(collection.aggregate(pipeline))
    
    if not results:
        print("No duplicates found (or insufficient data)")
        return
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Potential Duplicate Property:")
        print(f"   Location: ({result['_id']['lat_rounded']}, {result['_id']['lng_rounded']})")
        print(f"   Rooms: {result['_id']['rooms']}")
        print(f"   Operation: {result['_id']['operation_type']}")
        print(f"   Found in {len(result['platforms'])} platforms: {', '.join(result['platforms'])}")
        print(f"   Listings:")
        
        for listing in result['listings']:
            price_str = f"${listing['price']:,.0f} {listing['currency']}" if listing['price'] else "N/A"
            title = listing['title'][:50] if listing['title'] else 'N/A'
            print(f"     - [{listing['platform']}] {price_str} - {title}")


def query_3_price_analysis_by_zone(collection):
    """Analyze price distribution by neighborhood/zone"""
    print_section("QUERY 3: Price Analysis by Zone (Text Mining)")
    
    # Extract zone from address_text
    pipeline = [
        {"$match": {
            "operation_type": "sale",
            "price": {"$ne": None, "$gt": 0},
            "address_text": {"$ne": None}
        }},
        {"$addFields": {
            # Extract neighborhood (simple heuristic - words after last comma)
            "zone": {"$trim": {"input": {"$arrayElemAt": [
                {"$split": ["$address_text", ","]}, -1
            ]}}}
        }},
        {"$group": {
            "_id": "$zone",
            "avg_price": {"$avg": "$price"},
            "min_price": {"$min": "$price"},
            "max_price": {"$max": "$price"},
            "count": {"$sum": 1}
        }},
        {"$match": {"count": {"$gte": 3}}},  # At least 3 properties
        {"$sort": {"avg_price": -1}},
        {"$limit": 10}
    ]
    
    results = list(collection.aggregate(pipeline))
    
    if not results:
        print("Insufficient data for zone analysis")
        return
    
    print(f"{'Zone':<30} {'Avg Price':>15} {'Min':>15} {'Max':>15} {'Count':>8}")
    print("-" * 80)
    
    for result in results:
        zone = result['_id'][:28] if result['_id'] else 'Unknown'
        avg = result['avg_price']
        min_p = result['min_price']
        max_p = result['max_price']
        count = result['count']
        
        print(f"{zone:<30} ${avg:>13,.0f} ${min_p:>13,.0f} ${max_p:>13,.0f} {count:>8}")


def query_4_geospatial_nearby(collection):
    """Find properties near a specific point (geospatial query)"""
    print_section("QUERY 4: Properties Near Obelisco (Geospatial)")
    
    # Obelisco coordinates: -34.6037, -58.3816
    obelisco = [-58.3816, -34.6037]  # GeoJSON format: [lng, lat]
    radius_meters = 2000  # 2km radius
    
    # First, check if we have any properties with geo_location
    count_with_geo = collection.count_documents({"geo_location": {"$ne": None}})
    
    if count_with_geo == 0:
        print("No properties with geo_location field found.")
        print("Note: Existing documents need to be updated with geo_location field.")
        print("New ingestions will automatically include this field.")
        return
    
    pipeline = [
        {"$geoNear": {
            "near": {"type": "Point", "coordinates": obelisco},
            "distanceField": "distance",
            "maxDistance": radius_meters,
            "spherical": True,
            "query": {"operation_type": "sale"}
        }},
        {"$limit": 10}
    ]
    
    try:
        results = list(collection.aggregate(pipeline))
        
        if not results:
            print(f"No properties found within {radius_meters}m of Obelisco")
            return
        
        print(f"Found {len(results)} properties within 2km of Obelisco:\n")
        
        for i, doc in enumerate(results, 1):
            distance = doc.get('distance', 0) / 1000  # Convert to km
            title = doc.get('title', 'N/A')[:50] if doc.get('title') else 'N/A'
            price = doc.get('price', 0)
            currency = doc.get('currency', 'N/A')
            
            price_str = f"${price:,.0f} {currency}" if price else "N/A"
            print(f"{i}. {distance:.2f}km - {price_str} - {title}")
    
    except Exception as e:
        print(f"Geospatial query error: {e}")
        print("Make sure geo_location 2dsphere index exists.")


def query_5_text_search(collection):
    """Full-text search in titles and descriptions"""
    print_section("QUERY 5: Full-Text Search")
    
    search_term = "balcón terraza"
    
    print(f"Searching for: '{search_term}'\n")
    
    try:
        cursor = collection.find(
            {"$text": {"$search": search_term}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(5)
        
        results = list(cursor)
        
        if not results:
            print(f"No results found for '{search_term}'")
            return
        
        for i, doc in enumerate(results, 1):
            score = doc.get('score', 0)
            title = doc.get('title', 'N/A')[:60] if doc.get('title') else 'N/A'
            platform = doc.get('platform', 'N/A')
            price = doc.get('price', 0)
            currency = doc.get('currency', 'N/A')
            
            price_str = f"${price:,.0f} {currency}" if price else "N/A"
            print(f"{i}. [Score: {score:.2f}] [{platform}] {price_str}")
            print(f"   {title}")
            print()
    
    except Exception as e:
        print(f"Text search error: {e}")
        print("Make sure text index on (title, description) exists.")


def query_6_temporal_analysis(collection):
    """Analyze listing trends over time"""
    print_section("QUERY 6: Temporal Analysis - Recent Listings")
    
    # Last 7 days
    last_week = datetime.now() - timedelta(days=7)
    
    pipeline = [
        {"$match": {
            "ingested_at": {"$gte": last_week}
        }},
        {"$group": {
            "_id": {
                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$ingested_at"}},
                "platform": "$platform"
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.date": -1, "_id.platform": 1}}
    ]
    
    results = list(collection.aggregate(pipeline))
    
    if not results:
        print("No listings ingested in the last 7 days")
        return
    
    print(f"{'Date':<12} {'Platform':<15} {'Count':>8}")
    print("-" * 40)
    
    for result in results:
        date = result['_id']['date']
        platform = result['_id']['platform']
        count = result['count']
        
        print(f"{date:<12} {platform:<15} {count:>8}")


def main():
    """Run all example queries"""
    
    print("\n" + "=" * 80)
    print("PropScrape Data Lake - Query Examples".center(80))
    print("=" * 80)
    
    # Connect to MongoDB
    try:
        client = MongoClient(settings.DATABASE_URL, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
    except Exception as e:
        print(f"\n✗ ERROR: Could not connect to MongoDB: {e}")
        return 1
    
    db = client["propscrape"]
    collection = db["listings_current"]
    
    # Check if we have data
    total_count = collection.count_documents({})
    
    if total_count == 0:
        print("\n⚠ WARNING: Database is empty!")
        print("Run ingestion first to populate the data lake.")
        return 0
    
    print(f"\n✓ Connected to data lake ({total_count:,} listings)")
    
    # Run queries
    try:
        query_1_top_cheapest_cross_platform(collection)
        query_2_detect_duplicates(collection)
        query_3_price_analysis_by_zone(collection)
        query_4_geospatial_nearby(collection)
        query_5_text_search(collection)
        query_6_temporal_analysis(collection)
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        return 0
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        client.close()
    
    print("\n" + "=" * 80)
    print("✓ Query Examples Complete")
    print("=" * 80 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
