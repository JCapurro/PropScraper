from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, Text
from sqlalchemy.sql import func
from .database import Base

# --- Pydantic Models (Unified Listing Model) ---

class UnifiedListing(BaseModel):
    platform: str
    platform_listing_id: str
    listing_url: str
    operation_type: str  # rent, sale
    property_type: str   # apartment, house, etc.
    price: float
    currency: str
    expenses: Optional[float] = None
    address_text: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None
    surface_total: Optional[float] = None
    surface_covered: Optional[float] = None
    rooms: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    images: List[str] = []
    agent_publisher: Optional[str] = None
    status: str # active, delisted, paused
    source_created_at: Optional[datetime] = None
    source_updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# --- SQLAlchemy Models ---

class ListingDB(Base):
    __tablename__ = "listings_current"

    # Composite PK: platform + platform_listing_id is usually enough, 
    # but a surrogate ID is often cleaner. Let's use string ID as PK for now or a composite.
    # For MVP, let's stick to a simple strategy: id = platform + "_" + platform_listing_id
    id = Column(String, primary_key=True, index=True)
    
    platform = Column(String, index=True, nullable=False)
    platform_listing_id = Column(String, index=True, nullable=False)
    listing_url = Column(String)
    
    operation_type = Column(String, nullable=False)
    property_type = Column(String, nullable=False)
    
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    expenses = Column(Float, nullable=True)
    
    address_text = Column(String, nullable=True)
    geo_lat = Column(Float, nullable=True)
    geo_lng = Column(Float, nullable=True)
    
    surface_total = Column(Float, nullable=True)
    surface_covered = Column(Float, nullable=True)
    
    rooms = Column(Integer, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    # Store images as JSON array
    images = Column(JSON, nullable=True)
    
    agent_publisher = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")
    
    source_created_at = Column(DateTime, nullable=True)
    source_updated_at = Column(DateTime, nullable=True)
    ingested_at = Column(DateTime, server_default=func.now())
    
    raw_payload = Column(JSON, nullable=True)

class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, server_default=func.now())
    platform = Column(String)
    listings_processed = Column(Integer, default=0)
    listings_new = Column(Integer, default=0)
    listings_updated = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    status = Column(String) # started, completed, failed
