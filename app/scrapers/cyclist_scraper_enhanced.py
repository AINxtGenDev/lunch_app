# app/scrapers/cyclist_scraper_enhanced.py
import re
import os
import requests
import time
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from .base_scraper import BaseScraper


class CyclistScraperEnhanced(BaseScraper):
    """Enhanced scraper for Cyclist Cafe with multiple extraction methods."""
    
    def __init__(self):
        super().__init__(
            "Cyclist",
            "https://www.cafe-cyclist.com/"
        )
        self.base_url = self.url  # Alias for compatibility
        self.flipsnack_patterns = [
            "https://www.flipsnack.com/EE9BE6CC5A8/",
            "https://www.cafe-cyclist.com/",
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def setup_selenium_driver(self):
        """Setup headless Chrome driver for dynamic content."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            # Try to use system chromedriver first (for ARM compatibility)
            import shutil
            chromedriver_path = shutil.which('chromedriver')
            if chromedriver_path:
                service = Service(chromedriver_path)
            else:
                # Fall back to WebDriverManager
                service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome driver: {e}")
            return None
    
    def find_latest_menu_url(self) -> Optional[str]:
        """Find the latest menu URL using multiple strategies."""
        # Strategy 1: Check the main website for Flipsnack links
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for iframe with Flipsnack
                iframe = soup.find('iframe', src=lambda x: x and 'flipsnack.com' in x)
                if iframe:
                    return iframe['src']
                
                # Look for direct links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if 'flipsnack.com' in href and 'wochenmen' in href.lower():
                        self.logger.info(f"Found Flipsnack link: {href}")
                        return href
                        
        except Exception as e:
            self.logger.error(f"Error checking main website: {e}")
        
        # Strategy 2: Use Selenium to check for dynamically loaded content
        driver = None
        try:
            driver = self.setup_selenium_driver()
            if driver:  # Only proceed if driver was successfully created
                driver.get(self.base_url)
                time.sleep(3)  # Wait for dynamic content
                
                # Check for iframes
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    src = iframe.get_attribute('src')
                    if src and 'flipsnack.com' in src:
                        self.logger.info(f"Found Flipsnack iframe via Selenium: {src}")
                        return src
                        
                # Check for links
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute('href')
                    if href and 'flipsnack.com' in href and 'wochenmen' in href.lower():
                        self.logger.info(f"Found Flipsnack link via Selenium: {href}")
                        return href
            else:
                self.logger.warning("Selenium driver not available, skipping dynamic content check")
                    
        except Exception as e:
            self.logger.error(f"Error with Selenium: {e}")
        finally:
            if driver:
                driver.quit()
        
        # Strategy 3: Check known Flipsnack collection
        try:
            collection_url = "https://www.flipsnack.com/EE9BE6CC5A8/"
            response = requests.get(collection_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for collection items with dates
                items = soup.find_all(['a', 'div'], class_=lambda x: x and 'item' in x.lower())
                latest_date = None
                latest_url = None
                
                for item in items:
                    # Try to extract date from text or URL
                    text = item.get_text() if hasattr(item, 'get_text') else ''
                    href = item.get('href', '')
                    
                    # Look for date patterns
                    date_match = re.search(r'(\d{1,2})[-.](\d{1,2})[-.](\d{2,4})', text + href)
                    if date_match:
                        # Parse and compare dates to find the latest
                        # This is simplified; you might need more robust date parsing
                        if 'wochenmen' in (text + href).lower():
                            if item.name == 'a':
                                url = item['href']
                                if not url.startswith('http'):
                                    url = f"https://www.flipsnack.com{url}"
                                latest_url = url
                                break
                
                if latest_url:
                    self.logger.info(f"Found latest menu in collection: {latest_url}")
                    return latest_url
                    
        except Exception as e:
            self.logger.error(f"Error checking Flipsnack collection: {e}")
        
        # Fallback: Return a known working URL
        fallback_url = "https://www.flipsnack.com/EE9BE6CC5A8/wochenmen-14-20-08-2023/full-view.html"
        self.logger.warning(f"Using fallback URL: {fallback_url}")
        return fallback_url
    
    def extract_image_with_selenium(self, url: str) -> Optional[bytes]:
        """Use Selenium to capture the menu as an image."""
        driver = None
        try:
            driver = self.setup_selenium_driver()
            if not driver:
                self.logger.warning("Selenium driver not available for screenshot")
                return None
                
            driver.get(url)
            
            # Wait for the flipbook to load
            wait = WebDriverWait(driver, 15)
            
            # Try different selectors for the flipbook content
            selectors = [
                "div.flipsnack-book",
                "div.flipbook-container",
                "canvas",
                "div[data-page='1']",
                "img[src*='page_1']"
            ]
            
            element = None
            for selector in selectors:
                try:
                    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    if element:
                        break
                except:
                    continue
            
            if element:
                # Take screenshot of the element
                screenshot = element.screenshot_as_png
                self.logger.info("Successfully captured screenshot with Selenium")
                return screenshot
            else:
                # Take full page screenshot as fallback
                screenshot = driver.get_screenshot_as_png()
                self.logger.info("Captured full page screenshot as fallback")
                return screenshot
                
        except Exception as e:
            self.logger.error(f"Error capturing with Selenium: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def get_menu_image(self, url: str) -> Optional[bytes]:
        """Get menu image using multiple methods."""
        # Method 1: Try to get direct image URL from page
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check meta tags
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    image_url = og_image['content']
                    # Try to get higher resolution
                    image_url = image_url.replace('/medium', '/large').replace('/small', '/large')
                    
                    img_response = requests.get(image_url, headers=self.headers, timeout=15)
                    if img_response.status_code == 200:
                        self.logger.info(f"Downloaded image from: {image_url}")
                        return img_response.content
                        
        except Exception as e:
            self.logger.error(f"Error downloading direct image: {e}")
        
        # Method 2: Use Selenium to capture the page
        screenshot = self.extract_image_with_selenium(url)
        if screenshot:
            return screenshot
            
        return None
    
    def perform_ocr(self, image_data: bytes) -> Optional[str]:
        """Perform OCR on image data."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Preprocess image for better OCR
            # Convert to grayscale if needed
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Perform OCR with German language
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, lang='deu+eng', config=custom_config)
            
            self.logger.info(f"OCR extracted {len(text)} characters")
            return text
            
        except Exception as e:
            self.logger.error(f"OCR error: {e}")
            return None
    
    def parse_menu_from_text(self, text: str) -> Dict[str, List[Dict]]:
        """Parse menu items from OCR text."""
        menu_by_day = {}
        
        # Clean and normalize text
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line and len(line) > 2:
                lines.append(line)
        
        # Day mappings
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
        skip_next = False
        
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
                
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
            if any(x in line for x in ['****', '€€€€', 'Tagesteller', 'CYCLIST']):
                continue
            if re.match(r'^\d{1,2}\.\d{1,2}', line):  # Date patterns
                continue
            
            # This looks like a menu item
            if len(line) > 5:
                # Clean up common OCR mistakes
                line = line.replace('|', 'l')
                line = re.sub(r'\s+', ' ', line)
                
                # Check if next line might be continuation
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # If next line doesn't look like a new item or day
                    if (not any(d in next_line.upper() for d in days.keys()) and
                        not any(x in next_line for x in ['****', '€', 'PASTA', 'WOK', 'CHILI'])):
                        if len(next_line) > 3 and next_line[0].islower():
                            line += ' ' + next_line
                            skip_next = True
                
                current_items.append({
                    'name': line,
                    'description': ''
                })
        
        # Add last day
        if current_day and current_items:
            menu_by_day[current_day] = current_items
            
        return menu_by_day
    
    def get_date_range_from_text(self, text: str) -> Optional[Tuple[date, date]]:
        """Extract date range from menu text."""
        # Look for patterns like "11.08-17.08" or "11.08.-17.08."
        patterns = [
            r'(\d{1,2})\.(\d{1,2})\.?[\s-]+(\d{1,2})\.(\d{1,2})',
            r'(\d{1,2})\.(\d{1,2})\.?-(\d{1,2})\.(\d{1,2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                start_day, start_month = int(match.group(1)), int(match.group(2))
                end_day, end_month = int(match.group(3)), int(match.group(4))
                
                current_year = date.today().year
                try:
                    start_date = date(current_year, start_month, start_day)
                    end_date = date(current_year, end_month, end_day)
                    
                    if end_date < start_date:
                        end_date = date(current_year + 1, end_month, end_day)
                    
                    return start_date, end_date
                except ValueError:
                    continue
                    
        return None
    
    def scrape(self) -> Optional[List[Dict]]:
        """Main scraping method."""
        self.logger.info(f"Starting enhanced scrape for {self.name}")
        
        # Find the latest menu URL
        menu_url = self.find_latest_menu_url()
        if not menu_url:
            self.logger.error("Could not find menu URL")
            return self.fallback_to_hardcoded()
        
        # Get the menu image
        image_data = self.get_menu_image(menu_url)
        if not image_data:
            self.logger.error("Could not get menu image")
            return self.fallback_to_hardcoded()
        
        # Perform OCR
        menu_text = self.perform_ocr(image_data)
        if not menu_text:
            self.logger.error("OCR failed")
            return self.fallback_to_hardcoded()
        
        # Check if menu is current
        date_range = self.get_date_range_from_text(menu_text)
        if date_range:
            start_date, end_date = date_range
            today = date.today()
            if not (start_date <= today <= end_date):
                self.logger.warning(f"Menu might be outdated: {start_date} to {end_date}")
        
        # Parse the menu
        menu_by_day = self.parse_menu_from_text(menu_text)
        
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
            return self.fallback_to_hardcoded()
        
        return menu_items if menu_items else None
    
    def fallback_to_hardcoded(self) -> Optional[List[Dict]]:
        """Fallback to hardcoded menu when OCR fails."""
        self.logger.info("Using fallback hardcoded menu")
        
        today = date.today()
        weekday = today.strftime("%A").upper()
        
        # Last known good menu (from screenshot)
        fallback_menu = {
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
        if weekday in fallback_menu:
            for item in fallback_menu[weekday]:
                menu_items.append({
                    'menu_date': today,
                    'category': 'Main Dish (Fallback)',
                    'description': item['name'],
                    'price': ''
                })
        
        return menu_items if menu_items else None