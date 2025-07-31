"""
Henry (enjoyhenry.com) restaurant scraper implementation.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

from .base_scraper import BaseScraper
from .chrome_driver_setup import get_chrome_driver

logger = logging.getLogger(__name__)


class HenryScraper(BaseScraper):
    """Scraper for Henry restaurant menu."""
    
    def __init__(self):
        super().__init__(
            name="Henry BDO",
            url="https://www.enjoyhenry.com/menuplan-bdo/"
        )
    
    def extract_menu_items(self) -> List[Dict[str, Any]]:
        """
        Extract menu items from Henry BDO website.
        The menu has a clear structure with today's menu in a column with class 'today'.
        """
        menu_items = []
        driver = None
        
        try:
            # Initialize the driver using ARM64-compatible setup
            driver = get_chrome_driver()
            
            logger.info(f"Loading Henry menu page: {self.url}")
            driver.get(self.url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Get the page source and parse with BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find the today's menu column
            today_column = soup.find('div', class_='today')
            if not today_column:
                logger.warning("Could not find today's menu column")
                return menu_items
            
            logger.info("Found today's menu column")
            
            # Get today's date
            today = datetime.now().date()
            
            # Find all menu items in today's column
            menu_cells = today_column.find_all('div', class_='td-menu')
            logger.info(f"Found {len(menu_cells)} menu cells")
            
            for cell in menu_cells:
                try:
                    # Extract category from the menu-category div
                    category_elem = cell.find('div', class_='menu-category')
                    category = category_elem.get_text(strip=True) if category_elem else "Main Dish"
                    
                    # Extract menu name
                    name_elem = cell.find('div', class_='menu-name')
                    name = name_elem.get_text(strip=True) if name_elem else ""
                    
                    # Extract menu description
                    desc_elem = cell.find('div', class_='menu-desc')
                    description = ""
                    if desc_elem:
                        desc_text = desc_elem.get_text(strip=True)
                        # Skip empty descriptions or size indicators like "klein", "groß"
                        if desc_text and desc_text not in ['klein', 'groß', 'small', 'large']:
                            description = desc_text
                    
                    # Combine name and description
                    full_description = name
                    if description:
                        full_description += f" - {description}"
                    
                    # Extract price(s)
                    price_elems = cell.find_all('div', class_='menu-price')
                    prices = []
                    for price_elem in price_elems:
                        price_text = price_elem.get_text(strip=True)
                        if price_text:
                            prices.append(price_text)
                    
                    # If there are multiple prices (like for salad bar klein/groß), 
                    # create separate entries
                    if len(prices) > 1:
                        # Check if we have size descriptions
                        size_descs = []
                        for desc_elem in cell.find_all('div', class_='menu-desc'):
                            desc_text = desc_elem.get_text(strip=True)
                            if desc_text in ['klein', 'groß', 'small', 'large']:
                                size_descs.append(desc_text)
                        
                        # Create entries for each size/price combination
                        for i, price in enumerate(prices):
                            size_desc = ""
                            if i < len(size_descs):
                                size_desc = f" ({size_descs[i]})"
                            
                            item_description = full_description + size_desc
                            
                            menu_items.append({
                                'menu_date': today,
                                'category': category,
                                'description': item_description,
                                'price': price
                            })
                    else:
                        # Single price item
                        price = prices[0] if prices else None
                        
                        # Skip items without name
                        if not name or len(name.strip()) < 2:
                            continue
                        
                        menu_items.append({
                            'menu_date': today,
                            'category': category,
                            'description': full_description,
                            'price': price
                        })
                    
                except Exception as e:
                    logger.warning(f"Error processing menu cell: {e}")
                    continue
            
            logger.info(f"Extracted {len(menu_items)} menu items from Henry")
            
        except Exception as e:
            logger.error(f"Error scraping Henry: {str(e)}", exc_info=True)
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