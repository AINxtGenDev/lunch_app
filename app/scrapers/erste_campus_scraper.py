# app/scrapers/erste_campus_scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from datetime import date
from typing import List, Dict, Optional
from collections import OrderedDict

from .base_scraper import BaseScraper


class ErsteCampusScraper(BaseScraper):
    """Production-ready scraper for Erste Campus restaurant."""
    
    def __init__(self):
        super().__init__(
            "Erste Campus",
            "https://erstecampus.at/mealplan/2025/external/single/kantine-en.html"
        )
        self.allergen_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L', 'M', 'N', 'O', 'P', 'R']
        
    def scrape(self) -> Optional[List[Dict]]:
        """Scrape the weekly menu from Erste Campus."""
        self.logger.info(f"Starting scrape for {self.name}")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = None
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(self.url)
            
            # Wait for content to load
            time.sleep(5)
            
            # Get the current view's menu first
            menu_items = []
            current_menu = self._extract_current_view(driver)
            if current_menu:
                menu_items.extend(current_menu)
                
            self.logger.info(f"Successfully scraped {len(menu_items)} items from {self.name}")
            return menu_items if menu_items else None
            
        except Exception as e:
            self.logger.error(f"Error scraping {self.name}: {e}", exc_info=True)
            return None
        finally:
            if driver:
                driver.quit()
                
    def _extract_current_view(self, driver) -> List[Dict]:
        """Extract menu from the current view."""
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            lines = [line.strip() for line in body_text.split('\n') if line.strip()]
            
            # Find current date
            current_date = date.today()
            for line in lines[:20]:
                date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{2})', line)
                if date_match:
                    day, month, year = date_match.groups()
                    current_date = date(2000 + int(year), int(month), int(day))
                    break
                    
            menu_items = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                if line in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                    category = self._normalize_category(line)
                    i += 1
                    
                    while i < len(lines) and lines[i] not in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                        item_lines = []
                        price = ''
                        
                        while i < len(lines):
                            current_line = lines[i]
                            
                            if re.match(r'^€\s*\d+', current_line):
                                price = current_line
                                i += 1
                                break
                            elif self._is_allergen_line(current_line):
                                i += 1
                                break
                            elif current_line in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                                break
                            else:
                                item_lines.append(current_line)
                                i += 1
                                
                        if item_lines:
                            description = ' '.join(item_lines)
                            cleaned = self._clean_description(description)
                            if cleaned and len(cleaned) > 10:
                                menu_items.append({
                                    'menu_date': current_date,
                                    'category': category,
                                    'description': cleaned,
                                    'price': price
                                })
                else:
                    i += 1
                    
            return menu_items
            
        except Exception as e:
            self.logger.error(f"Error extracting menu: {e}")
            return []
            
    def _normalize_category(self, text: str) -> str:
        """Normalize category names."""
        return {
            'SOUP': 'Soup',
            'MAIN DISH': 'Main Dish',
            'DESSERTS': 'Dessert',
            'SALAD': 'Salad'
        }.get(text.upper(), 'Main Dish')
        
    def _is_allergen_line(self, line: str) -> bool:
        """Check if line contains only allergen codes."""
        chars = line.replace(' ', '')
        return len(chars) > 0 and all(c in self.allergen_codes for c in chars)
        
    def _clean_description(self, text: str) -> str:
        """Clean menu description."""
        # Filter out URLs
        if any(p in text.lower() for p in ['http', '.html', 'external']):
            return ""
            
        # Remove category labels and allergens
        text = re.sub(r'^(SOUP|MAIN DISH|DESSERTS?|SALAD)\s*', '', text, flags=re.I)
        text = re.sub(r'\s+[A-Z](\s+[A-Z])*\s*$', '', text)
        text = text.replace('/', ' / ')
        
        return ' '.join(text.split()).strip()
