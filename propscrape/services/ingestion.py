import logging
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from ..core.models import UnifiedListing, ListingDB, IngestionRun
from ..core.database import SessionLocal
from ..connectors.base import BaseConnector
from ..connectors.zonaprop import ZonapropConnector
from ..connectors.mercadolibre import MercadoLibreConnector

logger = logging.getLogger(__name__)

def get_connector(platform: str) -> BaseConnector:
    if platform == "zonaprop":
        return ZonapropConnector()
    elif platform == "mercadolibre":
        return MercadoLibreConnector()
    else:
        raise ValueError(f"Unknown platform: {platform}")

def save_listing(session: Session, listing: UnifiedListing):
    # Construct PK
    # Strategy: id = platform + "_" + platform_listing_id
    pk_id = f"{listing.platform}_{listing.platform_listing_id}"
    
    # Prepare data for DB
    data = listing.model_dump()
    data['id'] = pk_id
    
    # Handle JSON serialization for 'images' if backend doesn't support it automatically (SQLAlchemy with PG usually does)
    # But for safety in this snippet, let's leave it as list, assuming PG dialect handles it.
    
    # Create upsert stmt
    # We use valid SQLAlchemy syntax (generic upsert is tricky without dialect, assuming PG here or basic merge)
    
    # Simple merge for MVP compatibility across DBs (though PG specific upsert is better for concurrency)
    # existing = session.query(ListingDB).filter_by(id=pk_id).first()
    
    listing_db = ListingDB(**data)
    listing_db.ingested_at = datetime.utcnow()
    
    session.merge(listing_db)
    
    return True

def run_ingestion_job(platform: str):
    session = SessionLocal()
    run_record = IngestionRun(platform=platform, status="started")
    session.add(run_record)
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
