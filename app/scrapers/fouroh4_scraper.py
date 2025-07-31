"""
4oh4.at restaurant scraper implementation.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

from .base_scraper import BaseScraper
from .chrome_driver_setup import get_chrome_driver

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
            # Initialize the driver using ARM64-compatible setup
            driver = get_chrome_driver()
            
            # Load the iframe URL directly
            iframe_url = "https://4oh4.at/mealplan/2025/external/single/4oh4.html"
            logger.info(f"Loading iframe content from: {iframe_url}")
            
            driver.get(iframe_url)
            
            # Wait for meal cards to load
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "meal-card"))
                )
                # Additional wait for all cards to render
                time.sleep(2)
            except:
                logger.warning("Meal cards not found within timeout, proceeding anyway")
                time.sleep(5)  # Give more time for content to load
            
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
                    # Extract category from meal-card-header
                    category = "Main Dish"
                    header_elem = card.find('div', class_='meal-card-header')
                    if header_elem:
                        header_text = header_elem.get_text(strip=True)
                        if header_text:
                            # Map German categories to English
                            category_map = {
                                'Salat / Suppe': 'Salad / Soup',
                                'Hauptspeise': 'Main Dish',
                                'Pizza': 'Pizza',
                                'Dessert': 'Dessert'
                            }
                            category = category_map.get(header_text, header_text)
                    
                    # Extract title from meal-card-title (if present)
                    title = ""
                    title_elem = card.find('div', class_='meal-card-title')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                    
                    # Extract description from meal-card-text
                    description = ""
                    text_elem = card.find('div', class_='meal-card-text')
                    if text_elem:
                        # Get text and replace <br> tags with space
                        for br in text_elem.find_all('br'):
                            br.replace_with(' | ')
                        description = text_elem.get_text(strip=True)
                    
                    # Combine title and description
                    full_description = ""
                    if title and description:
                        full_description = f"{title} - {description}"
                    elif title:
                        full_description = title
                    elif description:
                        full_description = description
                    
                    # Extract price from meal-card-price
                    price = None
                    price_elem = card.find('div', class_='meal-card-price')
                    if price_elem:
                        # Look for text containing €
                        price_text = price_elem.get_text(strip=True)
                        if '€' in price_text:
                            price = price_text
                    
                    # Also check data-category attribute as fallback
                    if category == "Main Dish":  # Only use if no header found
                        data_category = card.get('data-category')
                        if data_category:
                            if data_category == "appetizer":
                                category = "Salad / Soup"
                            elif data_category == "main-dish":
                                category = "Main Dish"
                            elif data_category == "pizza":
                                category = "Pizza"
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