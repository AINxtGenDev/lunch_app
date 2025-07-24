# Example: scrapers/erste_campus.py
from bs4 import BeautifulSoup
import requests
from .base_scraper import BaseScraper

class ErsteCampusScraper(BaseScraper):
    def __init__(self):
        super().__init__("Erste Campus", "https://erstecampus.at/en/kantine-am-campus-menu/")
    
    def scrape(self):
        try:
            response = requests.get(self.url, timeout=10)
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Parse menu items (customize based on actual HTML structure)
            menu_data = {
                'date': datetime.now().date(),
                'items': {
                    'soup': self._extract_soup(soup),
                    'main_dish': self._extract_main(soup),
                    'dessert': self._extract_dessert(soup)
                }
            }
            return menu_data
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            return None