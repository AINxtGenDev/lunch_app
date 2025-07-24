"""
Base scraper class for all restaurant scrapers
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging
from typing import Dict, Optional, Any

class BaseScraper(ABC):
    """Abstract base class for all scrapers"""

    def __init__(self, restaurant_name: str, url: str):
        self.restaurant_name = restaurant_name
        self.url = url
        self.logger = logging.getLogger(f"{__name__}.{restaurant_name}")

    @abstractmethod
    def scrape(self) -> Optional[Dict[str, Any]]:
        """
        Scrape menu data from the restaurant website

        Returns:
            Dictionary with menu data or None if scraping failed
            Expected format:
            {
                'date': datetime.date,
                'items': {
                    'category': 'item_name' or {'name': 'item', 'price': 10.50}
                }
            }
        """
        pass

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate scraped data structure"""
        required_fields = ['date', 'items']
        return all(field in data for field in required_fields)
