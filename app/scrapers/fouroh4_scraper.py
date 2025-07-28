"""
4oh4.at restaurant scraper implementation.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class FourOh4Scraper(BaseScraper):
    """Scraper for 4oh4.at restaurant menu."""
    
    def __init__(self):
        super().__init__(
            name="4oh4",
            url="https://4oh4.at/lunch-menu/"
        )
    
    def extract_menu_items(self) -> List[Dict[str, Any]]:
        """
        Extract menu items from 4oh4.at website.
        The menu is loaded in an iframe pointing to /mealplan/2025/external/single/4oh4.html
        """
        menu_items = []
        driver = None
        
        try:
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Initialize the driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Load the iframe URL directly
            iframe_url = "https://4oh4.at/mealplan/2025/external/single/4oh4.html"
            logger.info(f"Loading iframe content from: {iframe_url}")
            
            driver.get(iframe_url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Get the page source and parse with BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find all meal cards
            meal_cards = soup.find_all('div', class_='meal-card')
            logger.info(f"Found {len(meal_cards)} meal cards")
            
            # Get today's date
            today = datetime.now().date()
            
            # Extract menu items from meal cards
            for card in meal_cards:
                try:
                    # Extract title from meal-card-title
                    title_elem = card.find('div', class_='meal-card-title')
                    title = title_elem.get_text(strip=True) if title_elem else "Unknown Dish"
                    
                    # Extract description from meal-card-text
                    text_elem = card.find('div', class_='meal-card-text')
                    description = ""
                    if text_elem:
                        # Get text and replace <br> tags with space
                        for br in text_elem.find_all('br'):
                            br.replace_with(' | ')
                        description = text_elem.get_text(strip=True)
                    
                    # Combine title and description
                    full_description = title
                    if description:
                        full_description += f" - {description}"
                    
                    # Extract price from meal-card-price
                    price = None
                    price_elem = card.find('div', class_='meal-card-price')
                    if price_elem:
                        price_span = price_elem.find('span')
                        if price_span:
                            price = price_span.get_text(strip=True)
                    
                    # Extract category from meal-card-header or data-category
                    category = "Main Dish"
                    header_elem = card.find('div', class_='meal-card-header')
                    if header_elem:
                        header_text = header_elem.get_text(strip=True)
                        if header_text:
                            category = header_text
                    
                    # Alternative: check data-category attribute
                    data_category = card.get('data-category')
                    if data_category:
                        if data_category == "appetizer":
                            category = "Salat / Suppe"
                        elif data_category == "main":
                            category = "Main Dish"
                        elif data_category == "dessert":
                            category = "Dessert"
                    
                    # Skip empty items
                    if not full_description or len(full_description.strip()) < 3:
                        continue
                    
                    menu_items.append({
                        'menu_date': today,
                        'category': category,
                        'description': full_description,
                        'price': price
                    })
                    
                except Exception as e:
                    logger.warning(f"Error processing meal card: {e}")
                    continue
            
            logger.info(f"Extracted {len(menu_items)} menu items from 4oh4")
            
        except Exception as e:
            logger.error(f"Error scraping 4oh4: {str(e)}", exc_info=True)
            raise
        
        finally:
            if driver:
                driver.quit()
        
        return menu_items
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method required by BaseScraper.
        """
        return self.extract_menu_items()