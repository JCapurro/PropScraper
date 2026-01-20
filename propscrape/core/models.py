from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, Text
from sqlalchemy.sql import func
from .database import Base

# --- Pydantic Models (Unified Listing Model) ---

class UnifiedListing(BaseModel):
    """Unified listing model for the data lake with flexible schema"""
    
    # Required fields
    platform: Literal["zonaprop", "mercadolibre", "properati", "argenprop"] = Field(
        description="Source platform identifier"
    )
    platform_listing_id: str = Field(description="Unique ID from source platform")
    listing_url: str = Field(description="URL to listing on source platform")
    operation_type: Literal["sale", "rent"] = Field(description="Type of operation")
    property_type: str = Field(description="Type of property (apartment, house, etc.)")
    currency: Literal["ARS", "USD", "EUR"] = Field(description="Currency code")
    status: Literal["active", "delisted", "paused", "sold", "rented"] = Field(
        default="active",
        description="Current listing status"
    )
    
    # Pricing
    price: Optional[float] = Field(default=None, ge=0, description="Listing price (non-negative)")
    expenses: Optional[float] = Field(default=None, ge=0, description="Monthly expenses")
    expenses_currency: Optional[Literal["ARS", "USD", "EUR"]] = Field(
        default=None,
        description="Currency code for expenses"
    )
    
    # Location
    address_text: Optional[str] = Field(default=None, description="Text address")
    geo_lat: Optional[float] = Field(default=None, ge=-90, le=90, description="Latitude")
    geo_lng: Optional[float] = Field(default=None, ge=-180, le=180, description="Longitude")
    
    # Property details
    surface_total: Optional[float] = Field(default=None, ge=0, description="Total surface (m²)")
    surface_covered: Optional[float] = Field(default=None, ge=0, description="Covered surface (m²)")
    rooms: Optional[int] = Field(default=None, ge=0, description="Number of rooms/ambientes")
    bedrooms: Optional[int] = Field(default=None, ge=0, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(default=None, ge=0, description="Number of bathrooms")
    
    # Content
    title: Optional[str] = Field(default=None, description="Listing title")
    description: Optional[str] = Field(default=None, description="Listing description")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    agent_publisher: Optional[str] = Field(default=None, description="Agent/publisher name")
    
    # Timestamps
    source_created_at: Optional[datetime] = Field(default=None, description="Created date on source")
    source_updated_at: Optional[datetime] = Field(default=None, description="Updated date on source")
    
    @field_validator('price', 'expenses', 'surface_total', 'surface_covered')
    @classmethod
    def validate_non_negative(cls, v: Optional[float]) -> Optional[float]:
        """Ensure numeric fields are non-negative"""
        if v is not None and v < 0:
            raise ValueError("Value must be non-negative")
        return v
    
    @field_validator('rooms', 'bedrooms', 'bathrooms')
    @classmethod
    def validate_count(cls, v: Optional[int]) -> Optional[int]:
        """Ensure count fields are non-negative integers"""
        if v is not None and v < 0:
            raise ValueError("Count must be non-negative")
        return v
    
    @model_validator(mode='after')
    def validate_coordinates(self) -> 'UnifiedListing':
        """Ensure both lat and lng are provided together or both None"""
        if (self.geo_lat is None) != (self.geo_lng is None):
            raise ValueError("Both geo_lat and geo_lng must be provided together or both None")
        return self
    
    def to_geojson_point(self) -> Optional[Dict[str, Any]]:
        """Convert coordinates to GeoJSON Point format for MongoDB geospatial queries"""
        if self.geo_lng is not None and self.geo_lat is not None:
            return {
                "type": "Point",
                "coordinates": [self.geo_lng, self.geo_lat]  # GeoJSON is [lng, lat]
            }
        return None
    
    def model_dump_with_geo(self, **kwargs) -> Dict[str, Any]:
        """Dump model to dict with geo_location field for MongoDB"""
        data = self.model_dump(**kwargs)
        geo_point = self.to_geojson_point()
        if geo_point:
            data['geo_location'] = geo_point
        return data
    
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
    
    price = Column(Float, nullable=True)
    currency = Column(String, nullable=False)
    expenses = Column(Float, nullable=True)
    expenses_currency = Column(String, nullable=True)
    
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
