#!/usr/bin/env python3
"""Debug the exact parser flow to understand why prices are missed."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.scrapers.erste_campus_scraper import ErsteCampusScraper
from app.scrapers.chrome_driver_setup import get_chrome_driver
from selenium.webdriver.common.by import By
import time
import re

def debug_parser_flow():
    """Debug the exact flow of the parser."""
    driver = None
    try:
        driver = get_chrome_driver()
        url = "https://erstecampus.at/mealplan/2025/external/single/kantine-en.html"
        driver.get(url)
        time.sleep(5)
        
        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = [line.strip() for line in body_text.split('\n') if line.strip()]
        
        # Create scraper instance to use its methods
        scraper = ErsteCampusScraper()
        
        print("=== SIMULATING PARSER FLOW ===\n")
        
        i = 0
        menu_items = []
        
        while i < len(lines):
            line = lines[i]
            
            if line in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                category = scraper._normalize_category(line)
                print(f"\n>>> Found category '{category}' at line {i}")
                i += 1
                
                while i < len(lines) and lines[i] not in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                    print(f"\n  Starting new item at line {i}")
                    item_lines = []
                    price = ''
                    description_complete = False
                    
                    while i < len(lines) and not description_complete:
                        current_line = lines[i]
                        print(f"    [{i:3d}]: {current_line}")
                        
                        if current_line in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                            print(f"         -> Hit next category, breaking")
                            description_complete = True
                            break
                        elif scraper._is_allergen_line(current_line):
                            print(f"         -> Allergen line detected")
                            description_complete = True
                            # Skip all consecutive allergen lines
                            while i < len(lines) and scraper._is_allergen_line(lines[i]):
                                print(f"         -> Skipping allergen: {lines[i]}")
                                i += 1
                            # After allergen lines, check if next line is a price
                            if i < len(lines) and re.match(r'^€\s*\d+', lines[i]):
                                price = lines[i]
                                print(f"         -> Found price after allergens: {price}")
                                i += 1
                        elif re.match(r'^€\s*\d+', current_line):
                            price = current_line
                            print(f"         -> Direct price found: {price}")
                            i += 1
                            description_complete = True
                        else:
                            item_lines.append(current_line)
                            print(f"         -> Added to description")
                            i += 1
                    
                    if item_lines:
                        description = ' '.join(item_lines)
                        print(f"  Complete item: desc='{description}', price='{price}'")
                        menu_items.append({
                            'category': category,
                            'description': description,
                            'price': price
                        })
            else:
                i += 1
        
        print(f"\n\nTotal items collected: {len(menu_items)}")
        main_dishes = [item for item in menu_items if item['category'] == 'Main Dish']
        print(f"Main dishes: {len(main_dishes)}")
        for dish in main_dishes:
            print(f"  - {dish['description'][:50]}... | Price: {dish['price'] or 'NONE'}")
            
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    debug_parser_flow()