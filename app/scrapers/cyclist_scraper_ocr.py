# app/scrapers/cyclist_scraper_ocr.py
import re
import os
import requests
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import io
from urllib.parse import urlparse, parse_qs

from .base_scraper import BaseScraper


class CyclistScraperOCR(BaseScraper):
    """Enhanced scraper for Cyclist Cafe that uses OCR to extract menu from Flipsnack images."""
    
    def __init__(self):
        super().__init__(
            "Cyclist",
            "https://www.cafe-cyclist.com/"
        )
        self.flipsnack_base = "https://www.flipsnack.com/EE9BE6CC5A8/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def get_latest_flipsnack_url(self) -> Optional[str]:
        """Find the latest Flipsnack menu URL from the Cyclist website or list."""
        try:
            # First try to get from the main website
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Look for Flipsnack links
                for link in soup.find_all('a', href=True):
                    if 'flipsnack.com' in link['href'] and 'wochenmen' in link['href'].lower():
                        self.logger.info(f"Found Flipsnack link on website: {link['href']}")
                        return link['href']
            
            # If not found on website, try to get the latest from Flipsnack collection
            collection_url = self.flipsnack_base
            response = requests.get(collection_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Look for the most recent menu
                for link in soup.find_all('a', href=True):
                    if 'wochenmen' in link['href'].lower():
                        full_url = f"https://www.flipsnack.com{link['href']}" if link['href'].startswith('/') else link['href']
                        self.logger.info(f"Found Flipsnack menu in collection: {full_url}")
                        return full_url
                        
        except Exception as e:
            self.logger.error(f"Error finding latest Flipsnack URL: {e}")
        
        # Fallback to a known URL pattern (will be updated as we discover new ones)
        return "https://www.flipsnack.com/EE9BE6CC5A8/wochenmen-14-20-08-2023/full-view.html"
    
    def get_menu_image_url(self, flipsnack_url: str) -> Optional[str]:
        """Extract the menu image URL from Flipsnack page."""
        try:
            response = requests.get(flipsnack_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch Flipsnack page: {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find the image URL from meta tags
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                image_url = og_image['content']
                # Get higher resolution version if available
                image_url = image_url.replace('/medium', '/large').replace('/small', '/large')
                self.logger.info(f"Found menu image URL: {image_url}")
                return image_url
                
            # Alternative: Look for data attributes or JavaScript variables
            # This would need more sophisticated parsing if the above doesn't work
            
        except Exception as e:
            self.logger.error(f"Error extracting image URL: {e}")
            
        return None
    
    def download_and_ocr_image(self, image_url: str) -> Optional[str]:
        """Download image and perform OCR to extract text."""
        try:
            response = requests.get(image_url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                self.logger.error(f"Failed to download image: {response.status_code}")
                return None
                
            # Open image with PIL
            image = Image.open(io.BytesIO(response.content))
            
            # Perform OCR with German language support
            # Make sure pytesseract and tesseract-ocr-deu are installed
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, lang='deu', config=custom_config)
            
            self.logger.info(f"OCR completed, extracted {len(text)} characters")
            return text
            
        except Exception as e:
            self.logger.error(f"Error during OCR: {e}")
            return None
    
    def parse_menu_text(self, text: str) -> Dict[str, List[Dict]]:
        """Parse the OCR text to extract menu items by day."""
        menu_by_day = {}
        
        # Clean up the text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Define day mappings in German and English
        day_mappings = {
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
        
        for i, line in enumerate(lines):
            # Check if line is a day
            line_upper = line.upper()
            if line_upper in day_mappings:
                # Save previous day's items
                if current_day and current_items:
                    menu_by_day[current_day] = current_items
                    current_items = []
                current_day = day_mappings[line_upper]
                continue
            
            # Skip price indicators and empty lines
            if line in ['****', '...', ''] or line.startswith('€'):
                continue
                
            # Check if this looks like a menu item (not a header or date)
            if current_day and len(line) > 5 and not re.match(r'^\d{1,2}\.\d{1,2}', line):
                # Check if this is the date range line
                if re.search(r'\d{1,2}\.\d{1,2}-\d{1,2}\.\d{1,2}', line):
                    continue
                    
                # This is likely a menu item
                # Try to combine with next line if it looks like a continuation
                description = line
                if i + 1 < len(lines) and not lines[i + 1].upper() in day_mappings:
                    next_line = lines[i + 1]
                    if not next_line.startswith('*') and not next_line.startswith('€'):
                        # Could be a continuation
                        if len(next_line) > 3 and not re.match(r'^\d', next_line):
                            description += ' ' + next_line
                
                current_items.append({
                    'name': description,
                    'description': ''
                })
        
        # Don't forget the last day
        if current_day and current_items:
            menu_by_day[current_day] = current_items
            
        return menu_by_day
    
    def extract_date_range(self, text: str) -> Optional[Tuple[date, date]]:
        """Extract the date range from the menu text."""
        # Look for pattern like "11.08-17.08" or "11.08.-17.08."
        pattern = r'(\d{1,2})\.(\d{1,2})\.?-(\d{1,2})\.(\d{1,2})\.?'
        match = re.search(pattern, text)
        
        if match:
            start_day, start_month = int(match.group(1)), int(match.group(2))
            end_day, end_month = int(match.group(3)), int(match.group(4))
            
            # Assume current year, but handle year boundary
            current_year = date.today().year
            start_date = date(current_year, start_month, start_day)
            end_date = date(current_year, end_month, end_day)
            
            # If end date is before start date, it's probably next year
            if end_date < start_date:
                end_date = date(current_year + 1, end_month, end_day)
                
            return start_date, end_date
            
        return None
    
    def is_menu_current(self, menu_text: str) -> bool:
        """Check if the menu is for the current week."""
        date_range = self.extract_date_range(menu_text)
        if not date_range:
            self.logger.warning("Could not extract date range from menu")
            return False
            
        start_date, end_date = date_range
        today = date.today()
        
        is_current = start_date <= today <= end_date
        self.logger.info(f"Menu date range: {start_date} to {end_date}, Today: {today}, Is current: {is_current}")
        
        return is_current
    
    def scrape(self) -> Optional[List[Dict]]:
        """Scrape the daily menu from Cyclist Cafe using OCR."""
        self.logger.info(f"Starting OCR-based scrape for {self.name}")
        
        # Get the latest Flipsnack URL
        flipsnack_url = self.get_latest_flipsnack_url()
        if not flipsnack_url:
            self.logger.error("Could not find Flipsnack menu URL")
            return None
            
        # Get the image URL from Flipsnack page
        image_url = self.get_menu_image_url(flipsnack_url)
        if not image_url:
            self.logger.error("Could not extract image URL from Flipsnack page")
            return None
            
        # Download and OCR the image
        menu_text = self.download_and_ocr_image(image_url)
        if not menu_text:
            self.logger.error("OCR failed to extract text from image")
            return None
            
        # Check if menu is current
        if not self.is_menu_current(menu_text):
            self.logger.warning("Menu appears to be outdated")
            # Continue anyway, but log the warning
            
        # Parse the menu text
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
            self.logger.info(f"Extracted {len(menu_items)} items for {weekday} using OCR")
        else:
            self.logger.warning(f"No menu found for {weekday} in OCR text")
            
        if menu_items:
            self.logger.info(f"Successfully prepared {len(menu_items)} items from {self.name}")
        else:
            self.logger.warning(f"No menu items found for {self.name}")
            
        return menu_items if menu_items else None