#!/usr/bin/env python3
"""
Test script for the Cyclist Cafe scraper.
Run this to verify the scraper is working correctly.
"""

import sys
import logging
from datetime import date

# Add the app directory to the Python path
sys.path.insert(0, '/home/nuc8/tmp/02_lunch_app/lunch_app')

# Configure logging with DEBUG level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.scrapers.cyclist_scraper import CyclistScraper

def test_cyclist_scraper():
    """Test the Cyclist Cafe scraper."""
    print("=" * 60)
    print("Testing Cyclist Cafe Scraper")
    print("=" * 60)
    
    scraper = CyclistScraper()
    print(f"Restaurant: {scraper.name}")
    print(f"URL: {scraper.url}")
    print(f"Menu URL: {scraper.menu_url}")
    print(f"Today's date: {date.today()}")
    print(f"Today is: {date.today().strftime('%A')}")
    print("-" * 60)
    
    try:
        print("Starting scrape...")
        menu_items = scraper.scrape()
        
        if menu_items:
            print(f"\n✅ Successfully scraped {len(menu_items)} menu items!")
            print("\nMenu items for today:")
            print("-" * 60)
            
            for i, item in enumerate(menu_items, 1):
                print(f"\nItem {i}:")
                print(f"  Date: {item['menu_date']}")
                print(f"  Category: {item['category']}")
                print(f"  Description: {item['description']}")
                if item.get('price'):
                    print(f"  Price: {item['price']}")
                    
        else:
            print("\n⚠️ No menu items found. This could mean:")
            print("  1. The menu for today is not available")
            print("  2. The website structure has changed")
            print("  3. There was an error accessing the website")
            
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_cyclist_scraper()