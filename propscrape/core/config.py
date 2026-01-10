from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./propscrape.db"
    ZONAPROP_API_KEY: Optional[str] = None
    MERCADOLIBRE_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
