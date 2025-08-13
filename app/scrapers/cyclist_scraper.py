# app/scrapers/cyclist_scraper.py
from datetime import date
from typing import List, Dict, Optional

from .base_scraper import BaseScraper


class CyclistScraper(BaseScraper):
    """Scraper for Cyclist Cafe restaurant.
    
    Note: The Flipsnack menu viewer doesn't expose text in a scrapable way,
    so this scraper uses a hardcoded weekly menu that needs to be updated manually.
    Future improvement: Integrate with an API or find an alternative menu source.
    """
    
    def __init__(self):
        super().__init__(
            "Cyclist",
            "https://www.cafe-cyclist.com/"
        )
        self.menu_url = "https://www.flipsnack.com/EE9BE6CC5A8/wochenmen-14-20-08-2023/full-view.html"
        
    def scrape(self) -> Optional[List[Dict]]:
        """Scrape the daily menu from Cyclist Cafe."""
        self.logger.info(f"Starting scrape for {self.name}")
        
        # Since the Flipsnack viewer doesn't expose the menu text in a scrapable way,
        # we'll use a hardcoded approach based on the visible menu from the screenshot
        # This should be updated weekly or integrated with an API if available
        
        today = date.today()
        weekday = today.strftime("%A").upper()
        
        # Weekly menu based on the screenshot (11.08-17.08)
        # This would need to be updated weekly
        weekly_menu = {
            "MONDAY": [
                {"name": "Minute Steak mit Senfmarinade", "description": ""},
                {"name": "Pasta mit Sonnengetrocknetes Tomatenpesto, Spinat, Paprika & Zucchini", "description": ""}
            ],
            "TUESDAY": [
                {"name": "Gegrilltes Hähnchen mit Teriyaki Sauce", "description": ""},
                {"name": "Wok - Gemüse mit Erbsen & Reis", "description": ""}
            ],
            "WEDNESDAY": [
                {"name": "Veganer Burger mit Falafel", "description": ""},
                {"name": "Chili sin Carne mit Reis, Tortilla Chips & Guacamole", "description": ""}
            ],
            "THURSDAY": [
                {"name": "Schweineschulter mit Zwiebelsauce", "description": ""},
                {"name": "Kartoffelknödel mit Ofentomate & Basilikum", "description": ""}
            ],
            "FRIDAY": [
                {"name": "Lachsfilet mit Zitronensauce", "description": ""},
                {"name": "Ratatouille mit Penne Aglio e Olio", "description": ""}
            ],
            "SATURDAY": [
                {"name": "Leberkäse & Putenleberkäse", "description": ""},
                {"name": "Grüne Bohnen mit Karotten & Röllgerste", "description": ""}
            ],
            "SUNDAY": [
                {"name": "Ofenkartoffel mit Pulled Chicken, gebratener Lachs & Gemüse", "description": ""},
                {"name": "Ofenkartoffel mit Käse, Gemüse & Kräuter", "description": ""}
            ]
        }
        
        menu_items = []
        
        # Get today's menu
        if weekday in weekly_menu:
            for item in weekly_menu[weekday]:
                menu_items.append({
                    'menu_date': today,
                    'category': 'Main Dish',
                    'description': item['name'],
                    'price': ''
                })
            self.logger.info(f"Using hardcoded menu for {weekday}")
        else:
            self.logger.warning(f"No menu available for {weekday}")
            
        if menu_items:
            self.logger.info(f"Successfully prepared {len(menu_items)} items from {self.name}")
        else:
            self.logger.warning(f"No menu items found for {self.name}")
            
        return menu_items if menu_items else None