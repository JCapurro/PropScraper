#!/usr/bin/env python3
"""
PropScraper - Main entry point
Multi-zone real estate scraper for creating a property data lake
"""

import sys
import os
import argparse

# Add parent directory to path to allow propscrape package imports when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from propscrape.services.ingestion import MultiZoneScraper, ZONES_CONFIG, OPERATION_TYPES
from propscrape.core.database import init_db

# Initialize database tables
init_db()

def main():
    parser = argparse.ArgumentParser(
        description="PropScraper - Multi-zone real estate data lake builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test with Capital Federal (5 pages)
  python main.py --test
  
  # Scrape all zones (full data lake)
  python main.py
  
  # Scrape specific zones
  python main.py --zones capital_federal zona_norte_gba
  
  # Scrape specific operations
  python main.py --operations sale rent
  
  # Limit pages per zone (for testing)
  python main.py --max-pages 3
  
  # Test without saving to database
  python main.py --test --no-db
        """
    )
    
    parser.add_argument(
        "--zones",
        nargs="+",
        help=f"Specific zones to scrape (default: all)",
        choices=list(ZONES_CONFIG.keys()),
        metavar="ZONE"
    )
    parser.add_argument(
        "--operations",
        nargs="+",
        help="Operation types to scrape (default: sale and rent)",
        choices=list(OPERATION_TYPES.keys()),
        metavar="OP"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum pages per zone (default: unlimited, get all data)",
        metavar="N"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Quick test run (Capital Federal only, 5 pages)"
    )
    parser.add_argument(
        "--no-db",
        action="store_true",
        help="Don't save to database (testing/debugging only)"
    )
    parser.add_argument(
        "--list-zones",
        action="store_true",
        help="List all available zones and exit"
    )
    
    args = parser.parse_args()
    
    # List available zones
    if args.list_zones:
        print("Available zones:")
        for key, config in ZONES_CONFIG.items():
            print(f"  {key:20s} - {config['display_name']:20s} ({config['description']})")
        print("\nAvailable operations:")
        for key, config in OPERATION_TYPES.items():
            print(f"  {key:20s} - {config['display_name']}")
        return 0
    
    print("\n" + "="*80)
    print("PropScraper - Real Estate Data Lake Builder")
    print("="*80)
    
    if args.test:
        print("Mode: QUICK TEST (Capital Federal only)")
    else:
        zones_list = args.zones or list(ZONES_CONFIG.keys())
        ops_list = args.operations or list(OPERATION_TYPES.keys())
        print(f"Mode: FULL SCRAPE")
        print(f"Zones to scrape: {len(zones_list)}")
        print(f"Operation types: {len(ops_list)}")
        print(f"Total combinations: {len(zones_list) * len(ops_list)}")
    
    print(f"Save to database: {'Yes' if not args.no_db else 'No'}")
    print(f"Max pages per zone: {args.max_pages or 'Unlimited (all pages)'}")
    print("="*80 + "\n")
    
    # Initialize scraper
    scraper = MultiZoneScraper()
    
    try:
        if args.test:
            print("[>] Starting quick test scrape...")
            stats = scraper.scrape_capital_federal_only(max_pages=args.max_pages or 5)
        else:
            zones = args.zones or list(ZONES_CONFIG.keys())
            operations = args.operations or list(OPERATION_TYPES.keys())
            
            print(f"[>] Starting scrape of {len(zones) * len(operations)} zone-operation combinations...")
            stats = scraper.scrape_all_zones_operations(
                zones=zones,
                operations=operations,
                max_pages_per_zone=args.max_pages,
                save_to_db=not args.no_db
            )
        
        print("\n[OK] Scraping completed successfully!")
        print(f"\nResults:")
        print(f"  Total listings: {stats['total_listings']}")
        print(f"  Combinations processed: {stats['total_operations_processed']}")
        print(f"  Errors: {stats['errors']}")
        
        scraper.close()
        return 0
    
    except KeyboardInterrupt:
        print("\n\n[!] Scraping interrupted by user")
        scraper.close()
        return 1
    except Exception as e:
        print(f"\n\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        scraper.close()
        return 1


if __name__ == "__main__":
    sys.exit(main())
