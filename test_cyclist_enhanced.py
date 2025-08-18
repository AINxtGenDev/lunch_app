#!/usr/bin/env python3
"""Quick test of the enhanced Cyclist scraper."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.cyclist_scraper_improved import CyclistScraperImproved

def main():
    print("Testing Enhanced Cyclist Scraper")
    print("=" * 50)
    
    scraper = CyclistScraperImproved()
    menu_items = scraper.scrape()
    
    if menu_items:
        # Separate by category
        daily_menu = [item for item in menu_items if item['category'] == 'MAIN DISH']
        tagesteller_info = [item for item in menu_items if item['category'] == 'TAGESTELLER']
        
        print(f"\nTotal items: {len(menu_items)}")
        print(f"Daily menu: {len(daily_menu)} items")
        print(f"TAGESTELLER: {len(tagesteller_info)} items")
        
        print("\nDAILY MENU:")
        for item in daily_menu:
            print(f"  • {item['description']} - {item['price']}")
        
        print("\nTAGESTELLER PRICING:")
        for item in tagesteller_info:
            print(f"  • {item['description']} - {item['price']}")
            
        print(f"\n✓ SUCCESS: Got {len(daily_menu)} daily + {len(tagesteller_info)} TAGESTELLER items")
    else:
        print("✗ FAILED: No menu items found")

if __name__ == "__main__":
    main()