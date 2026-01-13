"""
Multi-zone scraping ingestion service for PropScrape
Coordinates scraping of multiple Argentine zones and operation types
"""

import logging
import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from ..connectors.zonaprop import ZonapropConnector
from ..core.zones_config import ZONES_CONFIG, OPERATION_TYPES, ZONES_TO_SCRAPE, OPERATIONS_TO_SCRAPE
from ..core.database import SessionLocal
from ..core.models import ListingDB, IngestionRun


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MultiZoneScraper:
    """Orchestrates scraping across multiple zones and operation types"""
    
    def __init__(self):
        """Initialize the multi-zone scraper"""
        self.connector = ZonapropConnector()
        self.session = SessionLocal()
        self.stats = {
            "total_listings": 0,
            "total_zones_processed": 0,
            "total_operations_processed": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }
    
    def save_listing_to_db(self, listing) -> bool:
        """Save a listing to the database"""
        try:
            pk_id = f"{listing.platform}_{listing.platform_listing_id}"
            data = listing.model_dump()
            data['id'] = pk_id
            
            listing_db = ListingDB(**data)
            listing_db.ingested_at = datetime.utcnow()
            
            self.session.merge(listing_db)
            self.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving listing to DB: {e}")
            self.session.rollback()
            return False
    
    def scrape_zone_operation(self, zone_key: str, operation_key: str, 
                             max_pages: Optional[int] = None, save_to_db: bool = True) -> int:
        """
        Scrape a specific zone and operation combination
        
        Args:
            zone_key: Zone identifier
            operation_key: Operation type identifier
            max_pages: Maximum pages to scrape (None = all)
            save_to_db: Whether to save results to database
        
        Returns:
            Number of listings scraped
        """
        zone_config = ZONES_CONFIG.get(zone_key)
        operation_config = OPERATION_TYPES.get(operation_key)
        
        if not zone_config:
            logger.error(f"Zone '{zone_key}' not found in configuration")
            return 0
        
        if not operation_config:
            logger.error(f"Operation '{operation_key}' not found in configuration")
            return 0
        
        listings_count = 0
        
        try:
            logger.info(f"Starting: {zone_config['display_name']} - {operation_config['display_name']}")
            logger.info(f"Description: {zone_config['description']}")
            
            for listing in self.connector.fetch_listings_for_zone(zone_key, operation_key, max_pages):
                try:
                    if save_to_db:
                        self.save_listing_to_db(listing)
                    
                    listings_count += 1
                    
                    if listings_count % 10 == 0:
                        logger.info(f"  ✓ Processed {listings_count} listings")
                
                except Exception as e:
                    logger.error(f"Error processing listing: {e}")
                    self.stats["errors"] += 1
                    continue
            
            logger.info(f"Completed: {zone_config['display_name']} - {operation_config['display_name']} ({listings_count} listings)")
            self.stats["total_listings"] += listings_count
            self.stats["total_operations_processed"] += 1
            
            return listings_count
        
        except Exception as e:
            logger.error(f"Error scraping {zone_key} - {operation_key}: {e}")
            self.stats["errors"] += 1
            return 0
    
    def scrape_all_zones_operations(self, zones: Optional[List[str]] = None, 
                                   operations: Optional[List[str]] = None,
                                   max_pages_per_zone: Optional[int] = None,
                                   save_to_db: bool = True) -> dict:
        """
        Scrape all specified zones and operation combinations
        
        Args:
            zones: List of zone keys (None = all configured zones)
            operations: List of operation keys (None = all configured operations)
            max_pages_per_zone: Max pages per zone (None = all pages)
            save_to_db: Whether to save to database
        
        Returns:
            Statistics dictionary
        """
        zones = zones or ZONES_TO_SCRAPE
        operations = operations or OPERATIONS_TO_SCRAPE
        
        self.stats["start_time"] = datetime.utcnow()
        
        logger.info("="*80)
        logger.info(f"Starting multi-zone scraping at {self.stats['start_time']}")
        logger.info(f"Zones: {', '.join([ZONES_CONFIG[z]['display_name'] for z in zones])}")
        logger.info(f"Operations: {', '.join([OPERATION_TYPES[o]['display_name'] for o in operations])}")
        logger.info(f"Max pages per zone: {max_pages_per_zone or 'Unlimited'}")
        logger.info("="*80)
        
        total = len(zones) * len(operations)
        current = 0
        
        for zone_key in zones:
            for operation_key in operations:
                current += 1
                
                logger.info(f"\n[{current}/{total}] Processing zone-operation...")
                
                self.scrape_zone_operation(
                    zone_key, 
                    operation_key, 
                    max_pages=max_pages_per_zone,
                    save_to_db=save_to_db
                )
                
                self.stats["total_zones_processed"] += 1
        
        self.stats["end_time"] = datetime.utcnow()
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds() / 60
        
        logger.info("\n" + "="*80)
        logger.info("SCRAPING SUMMARY")
        logger.info("="*80)
        logger.info(f"Total listings scraped: {self.stats['total_listings']}")
        logger.info(f"Total zone-operation combinations processed: {self.stats['total_operations_processed']}")
        logger.info(f"Errors encountered: {self.stats['errors']}")
        logger.info(f"Duration: {duration:.2f} minutes")
        if duration > 0:
            logger.info(f"Average: {self.stats['total_listings']/duration:.2f} listings/minute")
        logger.info("="*80)
        
        if save_to_db:
            logger.info(f"Database updated successfully")
        
        return self.stats
    
    def scrape_capital_federal_only(self, max_pages: Optional[int] = 5) -> dict:
        """Quick scrape of Capital Federal for testing"""
        logger.info("Running quick test scrape: Capital Federal only")
        return self.scrape_all_zones_operations(
            zones=["capital_federal"],
            operations=["sale", "rent"],
            max_pages_per_zone=max_pages
        )
    
    def scrape_all_configured_zones(self, max_pages: Optional[int] = None) -> dict:
        """Scrape all configured zones"""
        logger.info("Scraping all configured zones with all operation types")
        return self.scrape_all_zones_operations(
            zones=ZONES_TO_SCRAPE,
            operations=OPERATIONS_TO_SCRAPE,
            max_pages_per_zone=max_pages
        )
    
    def close(self):
        """Close database session"""
        self.session.close()


def main():
    """Main entry point for multi-zone scraping"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Multi-zone real estate scraper for PropScrape data lake"
    )
    parser.add_argument(
        "--zones",
        nargs="+",
        help="Specific zones to scrape (default: all)",
        choices=list(ZONES_CONFIG.keys())
    )
    parser.add_argument(
        "--operations",
        nargs="+",
        help="Operation types to scrape (default: all)",
        choices=list(OPERATION_TYPES.keys())
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum pages per zone (default: unlimited)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Quick test run (Capital Federal only, 5 pages)"
    )
    parser.add_argument(
        "--no-db",
        action="store_true",
        help="Don't save to database (testing only)"
    )
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = MultiZoneScraper()
    
    try:
        if args.test:
            stats = scraper.scrape_capital_federal_only(max_pages=args.max_pages or 5)
        else:
            zones = args.zones or ZONES_TO_SCRAPE
            operations = args.operations or OPERATIONS_TO_SCRAPE
            
            stats = scraper.scrape_all_zones_operations(
                zones=zones,
                operations=operations,
                max_pages_per_zone=args.max_pages,
                save_to_db=not args.no_db
            )
        
        logger.info("Scraping completed successfully!")
        scraper.close()
        return 0
    
    except Exception as e:
        logger.error(f"Fatal error during scraping: {e}", exc_info=True)
        scraper.close()
        return 1


if __name__ == "__main__":
    exit(main())
    session.commit()
    
    try:
        connector = get_connector(platform)
        connector.authenticate()
        
        count_processed = 0
        
        for listing in connector.fetch_listings(): # Limit for demo
            if connector.validate_listing(listing):
                save_listing(session, listing)
                count_processed += 1
        
        run_record.status = "completed"
        run_record.listings_processed = count_processed
        session.commit()
        logger.info(f"Ingestion completed for {platform}. Processed: {count_processed}")
        
    except Exception as e:
        logger.error(f"Ingestion failed for {platform}: {e}", exc_info=True)
        run_record.status = "failed"
        run_record.errors += 1
        session.commit()
    finally:
        session.close()
