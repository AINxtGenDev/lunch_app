"""
Campus Bräu restaurant scraper implementation.
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


class CampusBrauScraper(BaseScraper):
    """Scraper for Campus Bräu restaurant menu."""
    
    def __init__(self):
        super().__init__(
            name="Campus Bräu",
            url="https://www.campusbraeu.at/"
        )
    
    def extract_menu_items(self) -> List[Dict[str, Any]]:
        """
        Extract menu items from Campus Bräu website.
        The menu has a weekly structure with daily items (soup, main course, dessert).
        """
        menu_items = []
        driver = None
        
        try:
            # Initialize the driver using ARM64-compatible setup
            driver = get_chrome_driver()
            
            logger.info(f"Loading Campus Bräu website: {self.url}")
            driver.get(self.url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Click on SPEISEKARTE link
            try:
                speisekarte_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "SPEISEKARTE"))
                )
                speisekarte_link.click()
                logger.info("Clicked on SPEISEKARTE link")
                
                # Wait for menu content to load
                time.sleep(3)
                
            except Exception as e:
                logger.warning(f"Could not click SPEISEKARTE link: {e}")
            
            # Get the page source and parse with BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Get today's date and determine current weekday
            today = datetime.now()
            weekday_map = {
                0: 'Montag',
                1: 'Dienstag',
                2: 'Mittwoch', 
                3: 'Donnerstag',
                4: 'Freitag'
            }
            
            current_weekday = weekday_map.get(today.weekday())
            
            # If it's weekend, default to Monday for testing
            if current_weekday is None:
                current_weekday = 'Montag'
                logger.info("Weekend detected, using Monday's menu")
            
            logger.info(f"Looking for menu for: {current_weekday}")
            
            # Find all day sections
            day_sections = soup.find_all('h3')
            
            for section in day_sections:
                day_name = section.get_text(strip=True)
                
                # Only process today's menu (or all days for comprehensive scraping)
                if day_name == current_weekday:
                    logger.info(f"Found section for {day_name}")
                    
                    # Find the menu items list after this heading
                    menu_list = section.find_next('ul')
                    if not menu_list:
                        continue
                    
                    # Extract menu items from the list
                    menu_list_items = menu_list.find_all('li')
                    
                    for item in menu_list_items:
                        try:
                            # Get category (Suppe, Hauptspeise, Nachspeise)
                            category_text = item.get_text(strip=True)
                            if not category_text:
                                continue
                            
                            # Extract category and description
                            detail_div = item.find('div', class_='detail')
                            if not detail_div:
                                continue
                            
                            description = detail_div.get_text(strip=True)
                            
                            # Clean up description (remove allergen codes and price spans)
                            # Remove price span content
                            price_span = detail_div.find('span', class_='price')
                            if price_span:
                                price_span.decompose()
                                description = detail_div.get_text(strip=True)
                            
                            # Determine category
                            category = "Main Dish"
                            category_lower = category_text.lower()
                            
                            if 'suppe' in category_lower:
                                category = "Soup"
                            elif 'hauptspeise' in category_lower:
                                category = "Main Dish"
                            elif 'nachspeise' in category_lower:
                                category = "Dessert"
                            
                            # Determine price based on category
                            price = None
                            if category == "Main Dish":
                                price = "€ 15,50"  # Mittagsmenü
                            elif category in ["Soup", "Dessert"]:
                                price = "€ 13,50"  # Tagesteller or included
                            
                            # Skip empty descriptions
                            if not description or len(description.strip()) < 5:
                                continue
                            
                            menu_items.append({
                                'menu_date': today.date(),
                                'category': category,
                                'description': description,
                                'price': price
                            })
                            
                            logger.debug(f"Added item: {category} - {description[:50]}...")
                            
                        except Exception as e:
                            logger.warning(f"Error processing menu item: {e}")
                            continue
                    
                    # Only process current day, break after finding it
                    break
            
            if not menu_items:
                logger.warning("No menu items found for current day, trying to extract all available days")
                
                # Fallback: extract all days if current day not found
                for day_name in weekday_map.values():
                    day_sections = soup.find_all('h3')
                    for section in day_sections:
                        if section.get_text(strip=True) == day_name:
                            menu_list = section.find_next('ul')
                            if menu_list:
                                menu_list_items = menu_list.find_all('li')
                                
                                for item in menu_list_items:
                                    try:
                                        detail_div = item.find('div', class_='detail')
                                        if detail_div:
                                            description = detail_div.get_text(strip=True)
                                            category_text = item.get_text(strip=True).split('\n')[0]
                                            
                                            category = "Main Dish"
                                            if 'suppe' in category_text.lower():
                                                category = "Soup"
                                                price = "€ 13,50"
                                            elif 'hauptspeise' in category_text.lower():
                                                category = "Main Dish"
                                                price = "€ 15,50"
                                            elif 'nachspeise' in category_text.lower():
                                                category = "Dessert"
                                                price = "€ 13,50"
                                            
                                            if description and len(description.strip()) > 5:
                                                menu_items.append({
                                                    'menu_date': today.date(),
                                                    'category': f"{category} ({day_name})",
                                                    'description': description,
                                                    'price': price
                                                })
                                    except Exception as e:
                                        continue
                            break
                    
                    # Limit to first few days to avoid too many items
                    if len(menu_items) >= 9:  # 3 items per day * 3 days
                        break
            
            logger.info(f"Extracted {len(menu_items)} menu items from Campus Bräu")
            
        except Exception as e:
            logger.error(f"Error scraping Campus Bräu: {str(e)}", exc_info=True)
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