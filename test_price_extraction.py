#!/usr/bin/env python3
"""Test the updated price extraction for main courses."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.scrapers.erste_campus_scraper import ErsteCampusScraper

def test_price_extraction():
    """Test that main course prices are being extracted correctly."""
    print("Testing Erste Campus scraper with price extraction...")
    print("=" * 60)
    
    scraper = ErsteCampusScraper()
    results = scraper.scrape()
    
    if results:
        print(f"\n✅ Successfully scraped {len(results)} menu items!")
        
        # Filter and show main dishes with prices
        main_dishes = [item for item in results if item['category'] == 'Main Dish']
        
        print(f"\n📋 Main Dishes found: {len(main_dishes)}")
        print("-" * 60)
        
        for i, item in enumerate(main_dishes, 1):
            print(f"\nMain Dish {i}:")
            print(f"  📅 Date: {item['menu_date']}")
            print(f"  📝 Description: {item['description']}")
            print(f"  💰 Price: {item['price'] or 'NO PRICE FOUND'}")
            
        # Count how many main dishes have prices
        dishes_with_prices = [d for d in main_dishes if d['price']]
        print(f"\n📊 Statistics:")
        print(f"  - Total main dishes: {len(main_dishes)}")
        print(f"  - Main dishes with prices: {len(dishes_with_prices)}")
        print(f"  - Main dishes without prices: {len(main_dishes) - len(dishes_with_prices)}")
        
        if len(dishes_with_prices) == 0:
            print("\n❌ WARNING: No main dishes have prices!")
        elif len(dishes_with_prices) < len(main_dishes):
            print("\n⚠️  WARNING: Some main dishes are missing prices!")
        else:
            print("\n✅ SUCCESS: All main dishes have prices!")
            
    else:
        print("\n❌ No results found!")

if __name__ == "__main__":
    test_price_extraction()