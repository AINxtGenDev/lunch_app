#!/usr/bin/env python3
"""Debug script to understand Café George menu structure"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
from app.scrapers.chrome_driver_setup import get_chrome_driver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_cafegeorge_structure():
    driver = None
    try:
        driver = get_chrome_driver()
        
        # Load the iframe URL directly
        iframe_url = "https://erstecampus.at/mealplan/2025/external/single/george-en.html"
        logger.info(f"Loading: {iframe_url}")
        
        driver.get(iframe_url)
        time.sleep(5)
        
        # Get the page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Check the current URL (might have date parameter)
        logger.info(f"Current URL: {driver.current_url}")
        
        # Get body text preview
        body = driver.find_element(By.TAG_NAME, "body")
        body_text = body.text[:1000]  # First 1000 chars
        logger.info(f"Body text preview:\n{body_text}")
        
        # Find meal cards
        meal_cards = soup.find_all('div', class_='meal-card')
        logger.info(f"Found {len(meal_cards)} meal cards")
        
        # If no meal cards, look for other structures
        if len(meal_cards) == 0:
            # Check for any divs with meal in class name
            meal_divs = soup.find_all('div', class_=lambda x: x and 'meal' in x)
            logger.info(f"Found {len(meal_divs)} divs with 'meal' in class name")
            
            # Check for content structure
            all_divs = soup.find_all('div')
            logger.info(f"Total div count: {len(all_divs)}")
            
            # Check for day tabs
            day_tabs = soup.find_all('button', class_='day-tab')
            logger.info(f"Found {len(day_tabs)} day tabs")
            if day_tabs:
                for tab in day_tabs[:5]:
                    logger.info(f"Day tab: {tab.get_text(strip=True)}")
        
        # Take a screenshot
        driver.save_screenshot("/home/nuc8/tmp/rpi_production/lunch_app/debug_cafegeorge_screenshot.png")
        logger.info("Screenshot saved as debug_cafegeorge_screenshot.png")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    debug_cafegeorge_structure()