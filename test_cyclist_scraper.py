#!/usr/bin/env python3
"""
Test script for Cyclist scraper - Tests the two-menu-per-day functionality
Run this to verify the cyclist_scraper_improved.py correctly shows 2 menus per day
"""

import sys
import os
from datetime import date, datetime

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.cyclist_scraper_improved import CyclistScraperImproved

def test_cyclist_scraper():
    """Test the Cyclist scraper"""
    print("=" * 60)
    print("CYCLIST SCRAPER TEST - TWO MENUS PER DAY")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Today is: {date.today().strftime('%A, %B %d, %Y')}")
    print("-" * 60)
    
    # Initialize the scraper
    scraper = CyclistScraperImproved()
    print(f"Scraper initialized: {scraper.name}")
    print(f"URL: {scraper.url}")
    print("-" * 60)
    
    # Test 1: Try to scrape actual menu
    print("\nTest 1: Attempting to scrape actual menu from website...")
    try:
        menu_items = scraper.scrape()
        
        if menu_items:
            print(f"✓ Successfully scraped {len(menu_items)} menu items")
            
            if len(menu_items) == 2:
                print("✓ CORRECT: Exactly 2 menu items (left and right column)")
            else:
                print(f"✗ WRONG: Expected 2 items, got {len(menu_items)}")
            
            print("\nMenu items for today:")
            print("-" * 40)
            for i, item in enumerate(menu_items, 1):
                print(f"\n📍 Menu {i} (Column {'Left' if i == 1 else 'Right'}):")
                print(f"   {item.get('description', 'N/A')}")
                print(f"   Price: {item.get('price', 'N/A')}")
        else:
            print("✗ No menu items returned from scraper")
    except Exception as e:
        print(f"✗ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    
    print("-" * 60)
    
    # Test 2: Test fallback menu
    print("\nTest 2: Testing fallback menu...")
    try:
        fallback_menu = scraper.get_fallback_menu()
        
        if fallback_menu:
            print(f"✓ Fallback menu has {len(fallback_menu)} items")
            
            if len(fallback_menu) == 2:
                print("✓ CORRECT: Exactly 2 menu items as expected!")
            else:
                print(f"✗ WRONG: Expected 2 items, got {len(fallback_menu)}")
            
            print("\nFallback menu items:")
            print("-" * 40)
            for i, item in enumerate(fallback_menu, 1):
                print(f"\n📍 Menu {i} (Column {'Left' if i == 1 else 'Right'}):")
                print(f"   {item.get('description', 'N/A')}")
                print(f"   Price: {item.get('price', 'N/A')}")
        else:
            print("✗ No fallback menu available")
    except Exception as e:
        print(f"✗ Error getting fallback menu: {e}")
        import traceback
        traceback.print_exc()
    
    print("-" * 60)
    
    # Test 3: Test menu parsing with sample two-column data
    print("\nTest 3: Testing menu parsing with two-column sample data...")
    
    # Simulate OCR output that has two columns
    sample_text = """
    Tagesteller
    11.08-17.08
    
    MONTAG                      MONTAG
    MINUTE STEAK                PASTA
    Senfmarinade                Sonnengetrocknetes Tomatenpesto,
                                Spinat, Paprika & Zucchini
    ****                        ****
    
    SONNTAG                     SONNTAG
    OFENKARTOFFEL               OFENKARTOFFEL
    Pulled Chicken,             Käse, Gemüse &
    gebratener Lachs            Kräuter
    & Gemüse
    ****                        ****
    """
    
    try:
        parsed_menu = scraper.parse_menu_intelligently(sample_text)
        
        print(f"Parsed {len(parsed_menu)} days from sample")
        
        for day_name in ['MONDAY', 'SUNDAY']:
            if day_name in parsed_menu:
                items = parsed_menu[day_name]
                print(f"\n{day_name}:")
                print(f"  Found {len(items)} items")
                
                if len(items) == 2:
                    print(f"  ✓ CORRECT: Exactly 2 items")
                    print(f"    Left column:  {items[0].get('name', 'N/A')}")
                    print(f"    Right column: {items[1].get('name', 'N/A')}")
                else:
                    print(f"  ✗ WRONG: Expected 2 items, got {len(items)}")
                    for i, item in enumerate(items, 1):
                        print(f"    Item {i}: {item.get('name', 'N/A')}")
    except Exception as e:
        print(f"✗ Error parsing sample menu: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("✅ The scraper should now display exactly TWO menu items per day")
    print("   - First item = Left column from original website")
    print("   - Second item = Right column from original website")
    print("\nExample for Sunday:")
    print("   1. OFENKARTOFFEL Pulled Chicken, gebratener Lachs & Gemüse")
    print("   2. OFENKARTOFFEL Käse, Gemüse & Kräuter")
    print("=" * 60)

def test_all_days_fallback():
    """Test fallback menu for all days of the week"""
    print("\n" + "=" * 60)
    print("TESTING ALL DAYS - FALLBACK MENU")
    print("=" * 60)
    
    scraper = CyclistScraperImproved()
    
    # Expected menus from the screenshot
    expected = {
        "MONDAY": 2,
        "TUESDAY": 2,
        "WEDNESDAY": 2,
        "THURSDAY": 2,
        "FRIDAY": 2,
        "SATURDAY": 2,
        "SUNDAY": 2
    }
    
    # Save original date
    import datetime
    original_date = date.today()
    
    for day_offset in range(7):
        test_date = original_date + datetime.timedelta(days=day_offset)
        weekday = test_date.strftime("%A").upper()
        
        # Mock the date for testing
        scraper.get_fallback_menu.__globals__['date'] = lambda: type('MockDate', (), {'today': lambda: test_date})()
        
        menu = scraper.get_fallback_menu()
        
        if menu:
            count = len(menu)
            expected_count = expected.get(weekday, 2)
            status = "✓" if count == expected_count else "✗"
            
            print(f"\n{weekday}:")
            print(f"  {status} {count} items (expected {expected_count})")
            
            if count == 2:
                print(f"  Left:  {menu[0]['description']} - {menu[0].get('price', 'N/A')}")
                print(f"  Right: {menu[1]['description']} - {menu[1].get('price', 'N/A')}")
            else:
                for i, item in enumerate(menu, 1):
                    print(f"  Item {i}: {item['description']} - {item.get('price', 'N/A')}")
        else:
            print(f"\n{weekday}: ✗ No menu available")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print("\nStarting Cyclist Scraper Tests...")
    print("This will test that the scraper returns exactly 2 menus per day")
    print("(corresponding to left and right columns on the website)\n")
    
    # Check for required packages
    try:
        from app.scrapers.cyclist_scraper_improved import CyclistScraperImproved
    except ImportError as e:
        print(f"✗ Error importing scraper: {e}")
        print("\nMake sure you're in the lunch_app directory and the scraper exists")
        sys.exit(1)
    
    # Run main test
    test_cyclist_scraper()
    
    # Test all days
    print("\n" + "-" * 60)
    print("Do you want to test all days of the week? (y/n): ", end="")
    try:
        response = input().strip().lower()
        if response == 'y':
            test_all_days_fallback()
    except:
        pass
    
    print("\nTest complete!")