"""
Data Quality Check Script
Analyzes data quality across the data lake and provides actionable insights
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from propscrape.core.config import settings
from datetime import datetime, timedelta


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


def check_missing_coordinates(collection):
    """Check for listings without geographic coordinates"""
    print_section("1. Missing Coordinates")
    
    total = collection.count_documents({})
    missing = collection.count_documents({
        "$or": [
            {"geo_lat": None},
            {"geo_lng": None},
            {"geo_lat": {"$exists": False}},
            {"geo_lng": {"$exists": False}}
        ]
    })
    
    percentage = (missing / total * 100) if total > 0 else 0
    
    print(f"Total listings: {total:,}")
    print(f"Missing coordinates: {missing:,} ({percentage:.1f}%)")
    
    if percentage > 0:
        # Breakdown by platform
        pipeline = [
            {"$match": {
                "$or": [
                    {"geo_lat": None},
                    {"geo_lng": None}
                ]
            }},
            {"$group": {
                "_id": "$platform",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        print("\nBy platform:")
        for result in results:
            print(f"  - {result['_id']}: {result['count']:,}")
    
    # Recommendation
    if percentage > 30:
        print("\n⚠ RECOMMENDATION: High percentage of listings without coordinates.")
        print("  Consider improving geocoding in connectors.")
    elif percentage > 0:
        print("\n✓ Acceptable level of missing coordinates.")


def check_missing_prices(collection):
    """Check for listings without price information"""
    print_section("2. Missing Prices")
    
    total = collection.count_documents({})
    missing = collection.count_documents({
        "$or": [
            {"price": None},
            {"price": {"$exists": False}},
            {"price": 0}
        ]
    })
    
    percentage = (missing / total * 100) if total > 0 else 0
    
    print(f"Total listings: {total:,}")
    print(f"Missing/zero prices: {missing:,} ({percentage:.1f}%)")
    
    if percentage > 0:
        # By platform and operation type
        pipeline = [
            {"$match": {
                "$or": [
                    {"price": None},
                    {"price": 0}
                ]
            }},
            {"$group": {
                "_id": {
                    "platform": "$platform",
                    "operation": "$operation_type"
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        print("\nBy platform and operation:")
        for result in results:
            platform = result['_id']['platform']
            operation = result['_id']['operation']
            count = result['count']
            print(f"  - {platform} ({operation}): {count:,}")
    
    if percentage > 10:
        print("\n⚠ WARNING: Significant number of listings without prices.")


def check_price_anomalies(collection):
    """Detect price anomalies (outliers)"""
    print_section("3. Price Anomalies")
    
    # Get price statistics by operation type
    for op_type in ["sale", "rent"]:
        pipeline = [
            {"$match": {
                "operation_type": op_type,
                "price": {"$ne": None, "$gt": 0}
            }},
            {"$group": {
                "_id": None,
                "avg": {"$avg": "$price"},
                "median": {"$percentile": {
                    "input": "$price",
                    "p": [0.5],
                    "method": "approximate"
                }} if hasattr(collection, '$percentile') else None,
                "min": {"$min": "$price"},
                "max": {"$max": "$price"},
                "count": {"$sum": 1}
            }}
        ]
        
        result = list(collection.aggregate(pipeline))
        
        if not result:
            continue
        
        stats = result[0]
        avg = stats.get('avg', 0)
        min_price = stats.get('min', 0)
        max_price = stats.get('max', 0)
        count = stats.get('count', 0)
        
        print(f"\n{op_type.upper()}:")
        print(f"  Count: {count:,}")
        print(f"  Average: ${avg:,.0f}")
        print(f"  Min: ${min_price:,.0f}")
        print(f"  Max: ${max_price:,.0f}")
        
        # Find extreme outliers (> 10x average or < 10% average)
        very_high = collection.count_documents({
            "operation_type": op_type,
            "price": {"$gt": avg * 10}
        })
        
        very_low = collection.count_documents({
            "operation_type": op_type,
            "price": {"$gt": 0, "$lt": avg * 0.1}
        })
        
        if very_high > 0:
            print(f"  ⚠ Suspiciously high: {very_high} (>10x average)")
        
        if very_low > 0:
            print(f"  ⚠ Suspiciously low: {very_low} (<10% average)")


def check_completeness_score(collection):
    """Calculate completeness score for each platform"""
    print_section("4. Data Completeness Score")
    
    # Important fields to check
    important_fields = [
        "price",
        "geo_lat",
        "geo_lng",
        "surface_total",
        "rooms",
        "title",
        "description"
    ]
    
    platforms = collection.distinct("platform")
    
    print(f"{'Platform':<15} {'Score':>8} {'Details'}")
    print("-" * 80)
    
    for platform in platforms:
        total = collection.count_documents({"platform": platform})
        
        if total == 0:
            continue
        
        field_scores = []
        
        for field in important_fields:
            has_field = collection.count_documents({
                "platform": platform,
                field: {"$ne": None, "$exists": True}
            })
            
            if field == "price":
                # Also exclude zeros
                has_field = collection.count_documents({
                    "platform": platform,
                    field: {"$ne": None, "$gt": 0}
                })
            
            percentage = (has_field / total * 100) if total > 0 else 0
            field_scores.append(percentage)
        
        avg_score = sum(field_scores) / len(field_scores)
        
        # Identify weakest field
        weakest_idx = field_scores.index(min(field_scores))
        weakest_field = important_fields[weakest_idx]
        weakest_score = field_scores[weakest_idx]
        
        print(f"{platform:<15} {avg_score:>7.1f}%  Weakest: {weakest_field} ({weakest_score:.0f}%)")
    
    print("\nScore interpretation:")
    print("  90-100%: Excellent")
    print("  75-89%: Good")
    print("  50-74%: Fair")
    print("  <50%: Poor - needs improvement")


def check_data_freshness(collection):
    """Check data freshness (when was data last ingested)"""
    print_section("5. Data Freshness")
    
    # Get latest ingestion by platform
    pipeline = [
        {"$group": {
            "_id": "$platform",
            "latest_ingestion": {"$max": "$ingested_at"},
            "oldest_ingestion": {"$min": "$ingested_at"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"latest_ingestion": -1}}
    ]
    
    results = list(collection.aggregate(pipeline))
    
    if not results:
        print("No data in collection")
        return
    
    now = datetime.now()
    
    print(f"{'Platform':<15} {'Latest Ingestion':<25} {'Age':>15} {'Total':>10}")
    print("-" * 80)
    
    for result in results:
        platform = result['_id']
        latest = result['latest_ingestion']
        count = result['count']
        
        if latest:
            age = now - latest
            age_str = f"{age.days}d {age.seconds//3600}h ago"
        else:
            age_str = "Unknown"
        
        latest_str = latest.strftime("%Y-%m-%d %H:%M:%S") if latest else "N/A"
        
        print(f"{platform:<15} {latest_str:<25} {age_str:>15} {count:>10,}")
    
    # Check for stale data (>7 days old)
    week_ago = now - timedelta(days=7)
    stale_count = collection.count_documents({
        "ingested_at": {"$lt": week_ago}
    })
    
    if stale_count > 0:
        total = collection.count_documents({})
        stale_percentage = (stale_count / total * 100) if total > 0 else 0
        
        print(f"\n⚠ {stale_count:,} listings ({stale_percentage:.1f}%) are older than 7 days")


def generate_summary_report(collection):
    """Generate overall summary"""
    print_section("6. Summary Report")
    
    total = collection.count_documents({})
    
    if total == 0:
        print("No data available for summary")
        return
    
    # By platform
    print("Listings by Platform:")
    platform_counts = collection.aggregate([
        {"$group": {"_id": "$platform", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    
    for result in platform_counts:
        platform = result['_id']
        count = result['count']
        percentage = (count / total * 100)
        print(f"  {platform:<15}: {count:>8,} ({percentage:>5.1f}%)")
    
    # By operation type
    print("\nListings by Operation:")
    op_counts = collection.aggregate([
        {"$group": {"_id": "$operation_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    
    for result in op_counts:
        op = result['_id']
        count = result['count']
        percentage = (count / total * 100)
        print(f"  {op:<15}: {count:>8,} ({percentage:>5.1f}%)")
    
    # Status distribution
    print("\nListings by Status:")
    status_counts = collection.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    
    for result in status_counts:
        status = result['_id']
        count = result['count']
        percentage = (count / total * 100)
        print(f"  {status:<15}: {count:>8,} ({percentage:>5.1f}%)")


def main():
    """Run data quality checks"""
    
    print("\n" + "=" * 80)
    print("PropScrape Data Lake - Data Quality Report".center(80))
    print("=" * 80)
    print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
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
        client.close()
        return 0
    
    print(f"\nTotal Listings in Data Lake: {total_count:,}")
    
    # Run checks
    try:
        check_missing_coordinates(collection)
        check_missing_prices(collection)
        check_price_anomalies(collection)
        check_completeness_score(collection)
        check_data_freshness(collection)
        generate_summary_report(collection)
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
    print("✓ Data Quality Report Complete")
    print("=" * 80 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
