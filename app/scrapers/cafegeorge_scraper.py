"""
Café George restaurant scraper implementation.
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


class CafeGeorgeScraper(BaseScraper):
    """Scraper for Café George restaurant menu."""
    
    def __init__(self):
        super().__init__(
            name="Café George",
            url="https://cafegeorge.at/en/weekly-menu-en/"
        )
    
    def extract_menu_items(self) -> List[Dict[str, Any]]:
        """
        Extract menu items from Café George website.
        The menu is loaded in an iframe pointing to erstecampus.at mealplan system.
        Note: Cafe George has WEEKLY specials and CLASSICS available all week,
        but no specific daily menus. On weekends, we return empty as there
        are no changing daily specials.
        """
        menu_items = []
        driver = None
        
        try:
            # Get today's date and check if it's a weekend
            today = datetime.now().date()
            weekday = today.weekday()  # Monday=0, Sunday=6
            is_weekend = weekday >= 5  # Saturday=5, Sunday=6
            
            # Cafe George doesn't have daily changing menus on weekends
            # Their WEEKLY and CLASSICS menus are static throughout the week
            # We only show menu for weekdays when there might be daily specials
            if is_weekend:
                logger.info(f"Today is {today.strftime('%A')} - Café George has no daily changing menu on weekends")
                return []  # Return empty list for weekends
            
            # Initialize the driver using ARM64-compatible setup
            driver = get_chrome_driver()
            
            # Load the iframe URL directly (same system as 4oh4)
            iframe_url = "https://erstecampus.at/mealplan/2025/external/single/george-en.html"
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
                        # Look for text containing €
                        price_text = price_elem.get_text(strip=True)
                        if '€' in price_text:
                            price = price_text
                    
                    # Extract category from meal-card-header
                    category = "Main Dish"
                    header_elem = card.find('div', class_='meal-card-header')
                    if header_elem:
                        header_text = header_elem.get_text(strip=True)
                        if header_text:
                            category = header_text
                    
                    # Map categories to more descriptive names
                    category_mapping = {
                        'Weekly': 'Weekly Special',
                        'Suppe': 'Soup',
                        'Salat': 'Salad',
                        'Hauptspeise': 'Main Dish',
                        'Vegetarisch': 'Vegetarian',
                        'Vegan': 'Vegan',
                        'Dessert': 'Dessert'
                    }
                    
                    # Apply category mapping
                    for key, value in category_mapping.items():
                        if key.lower() in category.lower():
                            category = value
                            break
                    
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
            
            logger.info(f"Extracted {len(menu_items)} menu items from Café George")
            
        except Exception as e:
            logger.error(f"Error scraping Café George: {str(e)}", exc_info=True)
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