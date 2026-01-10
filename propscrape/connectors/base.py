from abc import ABC, abstractmethod
from typing import List, Generator
from ..core.models import UnifiedListing

class BaseConnector(ABC):
    """
    Abstract base class for all platform connectors.
    """
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name

    @abstractmethod
    def authenticate(self):
        """
        Handle authentication (login, token refresh, etc.)
        """
        pass

    @abstractmethod
    def fetch_listings(self, **kwargs) -> Generator[UnifiedListing, None, None]:
        """
        Fetch listings from the source and yield UnifiedListing objects.
        Should handle pagination internally.
        """
        pass
        
    def validate_listing(self, listing: UnifiedListing) -> bool:
        """
        Optional validation logic specific to the connector before yielding.
        """
        return True
