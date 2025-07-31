#!/usr/bin/env python3
"""Add debug logging to understand why the scraper is missing prices."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from selenium.webdriver.common.by import By
import time
import re
from datetime import date
from typing import List, Dict, Optional

from app.scrapers.base_scraper import BaseScraper
from app.scrapers.chrome_driver_setup import get_chrome_driver


class DebugErsteCampusScraper(BaseScraper):
    """Debug version of Erste Campus scraper with extensive logging."""
    
    def __init__(self):
        super().__init__(
            "Erste Campus",
            "https://erstecampus.at/mealplan/2025/external/single/kantine-en.html"
        )
        self.allergen_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L', 'M', 'N', 'O', 'P', 'R']
        
    def scrape(self) -> Optional[List[Dict]]:
        driver = None
        try:
            driver = get_chrome_driver()
            driver.get(self.url)
            time.sleep(5)
            menu_items = self._extract_current_view(driver)
            return menu_items if menu_items else None
        finally:
            if driver:
                driver.quit()
                
    def _extract_current_view(self, driver) -> List[Dict]:
        """Extract menu from the current view with debug logging."""
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            lines = [line.strip() for line in body_text.split('\n') if line.strip()]
            
            current_date = date.today()
            for line in lines[:20]:
                date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{2})', line)
                if date_match:
                    day, month, year = date_match.groups()
                    current_date = date(2000 + int(year), int(month), int(day))
                    break
                    
            menu_items = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                if line in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                    category = self._normalize_category(line)
                    print(f"\n>>> Found category '{category}' at line {i}")
                    i += 1
                    
                    while i < len(lines) and lines[i] not in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                        print(f"\n  === Starting new item at line {i} ===")
                        item_lines = []
                        price = ''
                        
                        # First collect all description lines
                        description_complete = False
                        
                        while i < len(lines) and not description_complete:
                            current_line = lines[i]
                            print(f"    Line {i}: '{current_line}'")
                            
                            # Check if we've hit the next category - means current item is done
                            if current_line in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                                print(f"      -> Hit next category, breaking")
                                description_complete = True
                                break
                            # Check if this is an allergen line
                            elif self._is_allergen_line(current_line):
                                print(f"      -> Is allergen line")
                                # We've hit allergens, description is complete
                                description_complete = True
                                # Skip all consecutive allergen lines
                                allergen_count = 0
                                while i < len(lines) and self._is_allergen_line(lines[i]):
                                    print(f"      -> Skipping allergen at line {i}: '{lines[i]}'")
                                    allergen_count += 1
                                    i += 1
                                print(f"      -> Skipped {allergen_count} allergen lines, now at line {i}")
                                # After allergen lines, check if next line is a price
                                if i < len(lines):
                                    print(f"      -> Checking line {i} for price: '{lines[i]}'")
                                    if re.match(r'^€\s*\d+', lines[i]):
                                        price = lines[i]
                                        print(f"      -> FOUND PRICE: '{price}'")
                                        i += 1
                                    else:
                                        print(f"      -> Not a price line")
                            # Check if we've hit a price line directly (no allergens)
                            elif re.match(r'^€\s*\d+', current_line):
                                price = current_line
                                print(f"      -> Direct price found: '{price}'")
                                i += 1
                                description_complete = True
                            # Otherwise, it's part of the item description
                            else:
                                item_lines.append(current_line)
                                print(f"      -> Added to description")
                                i += 1
                                
                        if item_lines:
                            description = ' '.join(item_lines)
                            cleaned = self._clean_description(description)
                            print(f"  === Completed item ===")
                            print(f"      Description: '{cleaned}'")
                            print(f"      Price: '{price}' (empty={not price})")
                            if cleaned and len(cleaned) > 10:
                                menu_items.append({
                                    'menu_date': current_date,
                                    'category': category,
                                    'description': cleaned,
                                    'price': price
                                })
                                print(f"      -> Added to menu_items")
                            else:
                                print(f"      -> Skipped (description too short or empty)")
                else:
                    i += 1
                    
            return menu_items
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return []
            
    def _normalize_category(self, text: str) -> str:
        return {
            'SOUP': 'Soup',
            'MAIN DISH': 'Main Dish',
            'DESSERTS': 'Dessert',
            'SALAD': 'Salad'
        }.get(text.upper(), 'Main Dish')
        
    def _is_allergen_line(self, line: str) -> bool:
        chars = line.replace(' ', '')
        result = len(chars) > 0 and all(c in self.allergen_codes for c in chars)
        return result
        
    def _clean_description(self, text: str) -> str:
        if any(p in text.lower() for p in ['http', '.html', 'external']):
            return ""
        text = re.sub(r'^(SOUP|MAIN DISH|DESSERTS?|SALAD)\s*', '', text, flags=re.I)
        text = re.sub(r'\s+[A-Z](\s+[A-Z])*\s*$', '', text)
        text = text.replace('/', ' / ')
        return ' '.join(text.split()).strip()


def main():
    scraper = DebugErsteCampusScraper()
    results = scraper.scrape()
    
    print(f"\n\n=== FINAL RESULTS ===")
    print(f"Total items: {len(results) if results else 0}")
    
    if results:
        main_dishes = [item for item in results if item['category'] == 'Main Dish']
        print(f"Main dishes: {len(main_dishes)}")
        for i, dish in enumerate(main_dishes, 1):
            print(f"{i}. {dish['description'][:50]}... | Price: {dish['price'] or 'NONE'}")


if __name__ == "__main__":
    main()