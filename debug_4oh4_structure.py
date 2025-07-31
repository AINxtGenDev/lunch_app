#!/usr/bin/env python3
"""Debug script to understand 4oh4 meal card structure"""

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

def debug_4oh4_structure():
    driver = None
    try:
        driver = get_chrome_driver()
        
        # Load the iframe URL directly
        iframe_url = "https://4oh4.at/mealplan/2025/external/single/4oh4.html"
        logger.info(f"Loading: {iframe_url}")
        
        driver.get(iframe_url)
        time.sleep(5)
        
        # Get the page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find meal cards
        meal_cards = soup.find_all('div', class_='meal-card')
        logger.info(f"Found {len(meal_cards)} meal cards")
        
        # Analyze first few meal cards
        for i, card in enumerate(meal_cards[:3]):
            logger.info(f"\n=== Meal Card {i+1} ===")
            
            # Show the card's HTML structure
            logger.info(f"Card HTML preview:\n{str(card)[:300]}...")
            
            # Check all divs inside the card
            inner_divs = card.find_all('div')
            logger.info(f"Inner divs count: {len(inner_divs)}")
            
            # List all classes used
            all_classes = set()
            for elem in card.find_all(True):  # Find all elements
                if elem.get('class'):
                    all_classes.update(elem.get('class'))
            logger.info(f"Classes found: {all_classes}")
            
            # Get the text content
            text_content = card.get_text(separator=' | ', strip=True)
            logger.info(f"Text content: {text_content}")
            
            # Check for price elements
            price_elems = card.find_all(text=lambda text: '€' in text if text else False)
            logger.info(f"Price elements: {price_elems}")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    debug_4oh4_structure()