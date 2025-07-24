"""
Scrapers package initialization
"""

from typing import List, Type
from .base_scraper import BaseScraper

# Import all scraper classes here after implementing them
# from .erste_campus import ErsteCampusScraper
# from .four_oh_four import FourOhFourScraper
# from .enjoy_henry import EnjoyHenryScraper
# from .campus_braeu import CampusBraeuScraper
# from .flipsnack_menu import FlipsnackMenuScraper

def get_all_scrapers() -> List[Type[BaseScraper]]:
    """Get all available scraper classes"""
    return [
        # ErsteCampusScraper,
        # FourOhFourScraper,
        # EnjoyHenryScraper,
        # CampusBraeuScraper,
        # FlipsnackMenuScraper,
    ]

def run_all_scrapers():
    """Run all scrapers and save results to database"""
    # TODO: Implement this function
    pass
