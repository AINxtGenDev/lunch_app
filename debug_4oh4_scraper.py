#!/usr/bin/env python3
"""Debug script for 4oh4 scraper"""

import logging
from app.scrapers.chrome_driver_setup import get_chrome_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_4oh4():
    driver = None
    try:
        driver = get_chrome_driver()
        
        # Load the iframe URL directly
        iframe_url = "https://4oh4.at/mealplan/2025/external/single/4oh4.html"
        logger.info(f"Loading: {iframe_url}")
        
        driver.get(iframe_url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Get page source
        logger.info("Page title: %s", driver.title)
        logger.info("Current URL: %s", driver.current_url)
        
        # Try to find meal cards
        meal_cards = driver.find_elements(By.CLASS_NAME, "meal-card")
        logger.info(f"Found {len(meal_cards)} meal cards")
        
        # Get body text
        body = driver.find_element(By.TAG_NAME, "body")
        body_text = body.text[:500]  # First 500 chars
        logger.info(f"Body text preview: {body_text}")
        
        # Check for any divs
        divs = driver.find_elements(By.TAG_NAME, "div")
        logger.info(f"Found {len(divs)} div elements")
        
        # Check page source
        page_source = driver.page_source[:1000]
        logger.info(f"Page source preview: {page_source}")
        
        # Take a screenshot
        driver.save_screenshot("/home/nuc8/tmp/rpi_production/lunch_app/debug_4oh4_screenshot.png")
        logger.info("Screenshot saved as debug_4oh4_screenshot.png")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    debug_4oh4()