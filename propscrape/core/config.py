from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database configuration
    # Using MongoDB (change to sqlite:///./propscrape.db for SQLite)
    DATABASE_URL: str = "mongodb://localhost:27017/"
    
    DATABASE_TYPE: str = "mongodb"  # "mongodb" or "sqlite"
    
    ZONAPROP_API_KEY: Optional[str] = None
    MERCADOLIBRE_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
