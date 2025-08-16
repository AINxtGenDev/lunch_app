# app/scrapers/cyclist_scraper_simple_ocr.py
"""
Simplified OCR-based Cyclist scraper without Selenium dependency.
Optimized for Raspberry Pi and systems where Selenium is problematic.
"""
import re
import requests
from datetime import date
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import io

from .base_scraper import BaseScraper


class CyclistScraperSimpleOCR(BaseScraper):
    """Simplified OCR scraper for Cyclist Cafe - no Selenium required."""
    
    def __init__(self):
        super().__init__(
            "Cyclist",
            "https://www.cafe-cyclist.com/"
        )
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36'
        }
        
    def get_menu_image_url(self) -> Optional[str]:
        """Get the menu image URL directly from Flipsnack."""
        # Known Flipsnack URLs - update this list as new menus are published
        known_urls = [
            "https://www.flipsnack.com/EE9BE6CC5A8/wochenmen-14-20-08-2023/full-view.html",
            # Add more URLs here as they become available
        ]
        
        for url in known_urls:
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract image URL from meta tags
                    og_image = soup.find('meta', property='og:image')
                    if og_image and og_image.get('content'):
                        image_url = og_image['content']
                        # Get higher resolution
                        image_url = image_url.replace('/medium', '/large').replace('/small', '/large')
                        self.logger.info(f"Found image URL: {image_url}")
                        return image_url
                        
            except Exception as e:
                self.logger.error(f"Error checking {url}: {e}")
                continue
                
        return None
    
    def perform_ocr(self, image_data: bytes) -> Optional[str]:
        """Perform OCR on image data with preprocessing."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to grayscale for better OCR
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Perform OCR
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, lang='deu+eng', config=custom_config)
            
            self.logger.info(f"OCR extracted {len(text)} characters")
            return text
            
        except Exception as e:
            self.logger.error(f"OCR error: {e}")
            return None
    
    def parse_menu_text(self, text: str) -> Dict[str, List[Dict]]:
        """Parse OCR text to extract menu items."""
        menu_by_day = {}
        
        lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 2]
        
        days = {
            'MONTAG': 'MONDAY',
            'DIENSTAG': 'TUESDAY',
            'MITTWOCH': 'WEDNESDAY',
            'DONNERSTAG': 'THURSDAY',
            'FREITAG': 'FRIDAY',
            'SAMSTAG': 'SATURDAY',
            'SONNTAG': 'SUNDAY'
        }
        
        current_day = None
        current_items = []
        
        for line in lines:
            line_upper = line.upper()
            
            # Check for day
            for german_day, english_day in days.items():
                if german_day in line_upper:
                    if current_day and current_items:
                        menu_by_day[current_day] = current_items
                    current_day = english_day
                    current_items = []
                    break
            
            # Skip non-menu lines
            if not current_day:
                continue
            if any(x in line for x in ['****', '€€€€', 'Tagesteller']):
                continue
            if re.match(r'^\d{1,2}\.\d{1,2}', line):
                continue
            
            # Add menu item
            if len(line) > 5:
                current_items.append({
                    'name': line,
                    'description': ''
                })
        
        if current_day and current_items:
            menu_by_day[current_day] = current_items
            
        return menu_by_day
    
    def scrape(self) -> Optional[List[Dict]]:
        """Main scraping method."""
        self.logger.info(f"Starting simple OCR scrape for {self.name}")
        
        # Get image URL
        image_url = self.get_menu_image_url()
        if not image_url:
            self.logger.warning("Could not find image URL, using fallback")
            return self.get_fallback_menu()
        
        # Download image
        try:
            response = requests.get(image_url, headers=self.headers, timeout=20)
            if response.status_code != 200:
                self.logger.error(f"Failed to download image: {response.status_code}")
                return self.get_fallback_menu()
            image_data = response.content
        except Exception as e:
            self.logger.error(f"Error downloading image: {e}")
            return self.get_fallback_menu()
        
        # Perform OCR
        menu_text = self.perform_ocr(image_data)
        if not menu_text:
            self.logger.error("OCR failed")
            return self.get_fallback_menu()
        
        # Parse menu
        menu_by_day = self.parse_menu_text(menu_text)
        
        # Get today's menu
        today = date.today()
        weekday = today.strftime("%A").upper()
        
        menu_items = []
        if weekday in menu_by_day:
            for item in menu_by_day[weekday]:
                menu_items.append({
                    'menu_date': today,
                    'category': 'Main Dish',
                    'description': item['name'],
                    'price': ''
                })
            self.logger.info(f"Extracted {len(menu_items)} items for {weekday}")
        else:
            self.logger.warning(f"No menu found for {weekday}")
            return self.get_fallback_menu()
        
        return menu_items if menu_items else None
    
    def get_fallback_menu(self) -> Optional[List[Dict]]:
        """Fallback hardcoded menu."""
        self.logger.info("Using fallback menu")
        
        today = date.today()
        weekday = today.strftime("%A").upper()
        
        fallback_menu = {
            "MONDAY": [
                {"name": "Minute Steak mit Senfmarinade"},
                {"name": "Pasta mit Sonnengetrocknetes Tomatenpesto, Spinat, Paprika & Zucchini"}
            ],
            "TUESDAY": [
                {"name": "Gegrilltes Hähnchen mit Teriyaki Sauce"},
                {"name": "Wok - Gemüse mit Erbsen & Reis"}
            ],
            "WEDNESDAY": [
                {"name": "Veganer Burger mit Falafel"},
                {"name": "Chili sin Carne mit Reis, Tortilla Chips & Guacamole"}
            ],
            "THURSDAY": [
                {"name": "Schweineschulter mit Zwiebelsauce"},
                {"name": "Kartoffelknödel mit Ofentomate & Basilikum"}
            ],
            "FRIDAY": [
                {"name": "Lachsfilet mit Zitronensauce"},
                {"name": "Ratatouille mit Penne Aglio e Olio"}
            ],
            "SATURDAY": [
                {"name": "Leberkäse & Putenleberkäse"},
                {"name": "Grüne Bohnen mit Karotten & Röllgerste"}
            ],
            "SUNDAY": [
                {"name": "Ofenkartoffel mit Pulled Chicken, gebratener Lachs & Gemüse"},
                {"name": "Ofenkartoffel mit Käse, Gemüse & Kräuter"}
            ]
        }
        
        menu_items = []
        if weekday in fallback_menu:
            for item in fallback_menu[weekday]:
                menu_items.append({
                    'menu_date': today,
                    'category': 'Main Dish (Fallback)',
                    'description': item['name'],
                    'price': ''
                })
        
        return menu_items if menu_items else None