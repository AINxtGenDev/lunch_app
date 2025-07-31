#!/usr/bin/env python3
"""Test the actual scraper's _extract_current_view method directly."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.scrapers.erste_campus_scraper import ErsteCampusScraper
from app.scrapers.chrome_driver_setup import get_chrome_driver
import json

def test_extract_method():
    """Test the _extract_current_view method directly."""
    driver = None
    try:
        driver = get_chrome_driver()
        url = "https://erstecampus.at/mealplan/2025/external/single/kantine-en.html"
        driver.get(url)
        
        import time
        time.sleep(5)
        
        scraper = ErsteCampusScraper()
        results = scraper._extract_current_view(driver)
        
        print(f"Total items extracted: {len(results)}")
        print("\nAll items:")
        for i, item in enumerate(results, 1):
            print(f"\n{i}. {item['category']}:")
            print(f"   Date: {item['menu_date']}")
            print(f"   Description: {item['description']}")
            print(f"   Price: {item['price'] or 'NO PRICE'}")
        
        # Focus on main dishes
        main_dishes = [item for item in results if item['category'] == 'Main Dish']
        print(f"\n\nMain dishes summary: {len(main_dishes)} items")
        dishes_with_prices = [d for d in main_dishes if d['price']]
        print(f"Main dishes with prices: {len(dishes_with_prices)}")
        print(f"Main dishes without prices: {len(main_dishes) - len(dishes_with_prices)}")
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_extract_method()