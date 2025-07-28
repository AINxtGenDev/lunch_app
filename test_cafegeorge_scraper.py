#!/usr/bin/env python3
"""Test script for Café George scraper with detailed debugging"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.cafegeorge_scraper import CafeGeorgeScraper
from datetime import datetime

def test_cafegeorge_scraper():
    """Test the Café George scraper with detailed output"""
    
    print("=== Testing Café George Scraper ===")
    
    try:
        scraper = CafeGeorgeScraper()
        print(f"Scraper name: {scraper.name}")
        print(f"Scraper URL: {scraper.url}")
        
        print("\n=== Extracting menu items ===")
        menu_items = scraper.extract_menu_items()
        
        print(f"✓ Extracted {len(menu_items)} menu items")
        
        if menu_items:
            print("\n=== Menu Items ===")
            
            # Group by category
            categories = {}
            for item in menu_items:
                cat = item['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(item)
            
            # Display by category
            for category, items in sorted(categories.items()):
                print(f"\n{category}:")
                for item in items:
                    desc = item['description']
                    if len(desc) > 60:
                        desc = desc[:57] + "..."
                    print(f"  - {desc:<60} {item['price']}")
        
        print("\n=== Testing full scraper ===")
        all_items = scraper.scrape()
        print(f"✓ Full scraper returned {len(all_items)} items")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cafegeorge_scraper()