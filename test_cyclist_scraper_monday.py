#!/usr/bin/env python3
"""
Test the Cyclist scraper for Monday, September 1, 2025
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.cyclist_scraper_production import CyclistScraperProduction
from datetime import date

def test_cyclist_scraper():
    """Test the Cyclist scraper for today's menu."""
    print("\n" + "="*80)
    print("Testing Cyclist Scraper")
    print("="*80)
    print(f"📅 Today's date: {date.today().strftime('%A, %B %d, %Y')}")
    print("-"*80)
    
    # Create scraper instance
    scraper = CyclistScraperProduction()
    
    # Run the scraper
    print("\n🚀 Running scraper...")
    menu_items = scraper.scrape()
    
    if menu_items:
        print(f"\n✅ SUCCESS: Found {len(menu_items)} menu items")
        print("\n📋 Today's Menu:")
        print("-"*80)
        
        # Group items by category
        categories = {}
        for item in menu_items:
            category = item.get('category', 'UNKNOWN')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Display items by category
        for category, items in categories.items():
            print(f"\n{category}:")
            for item in items:
                description = item.get('description', 'No description')
                price = item.get('price', '')
                if price:
                    print(f"  • {description} - {price}")
                else:
                    print(f"  • {description}")
        
        # Check for expected Monday items
        print("\n🎯 Checking for expected Monday items:")
        expected_items = [
            "MINUTE STEAK Pepper sauce",
            "RATATOUILLE Polenta"
        ]
        
        descriptions = [item.get('description', '') for item in menu_items]
        for expected in expected_items:
            if expected in descriptions:
                print(f"  ✅ Found: {expected}")
            else:
                # Check partial matches
                found = False
                for desc in descriptions:
                    if 'STEAK' in desc.upper() and 'MINUTE' in expected.upper():
                        print(f"  ✅ Found (similar): {desc}")
                        found = True
                        break
                    elif 'RATATOUILLE' in desc.upper() and 'RATATOUILLE' in expected.upper():
                        print(f"  ✅ Found (similar): {desc}")
                        found = True
                        break
                if not found:
                    print(f"  ❌ Missing: {expected}")
        
    else:
        print("\n❌ FAILED: No menu items found")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_cyclist_scraper()