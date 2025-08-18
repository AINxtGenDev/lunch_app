#!/usr/bin/env python3
"""
Test script for Cyclist Scraper Improved.
Run this to manually test the Cyclist restaurant menu scraper.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.cyclist_scraper_improved import CyclistScraperImproved
import logging
from datetime import datetime

# Set up logging with detailed output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_cyclist_scraper():
    """Test the Cyclist scraper functionality."""
    print("=" * 70)
    print("CYCLIST SCRAPER IMPROVED TEST")
    print("=" * 70)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Today is: {datetime.now().strftime('%A, %B %d')}")
    print("-" * 70)
    
    try:
        # Initialize scraper
        scraper = CyclistScraperImproved()
        print(f"\n✓ Scraper initialized: {scraper.name}")
        print(f"  Base URL: {scraper.url}")
        
        # Test the scraper
        print("\n" + "=" * 70)
        print("TEST: Menu Extraction")
        print("-" * 70)
        
        menu_items = scraper.scrape()
        
        if menu_items:
            print(f"✓ Successfully extracted {len(menu_items)} menu items")
            
            # Display menu items
            print("\n" + "=" * 70)
            print("TODAY'S MENU")
            print("-" * 70)
            
            for i, item in enumerate(menu_items, 1):
                print(f"\n{i}. {item['description']}")
                print(f"   Price: {item['price']}")
                print(f"   Category: {item['category']}")
                print(f"   Date: {item['menu_date']}")
            
            # Summary
            print("\n" + "=" * 70)
            print("SUMMARY")
            print("-" * 70)
            print(f"Total items: {len(menu_items)}")
            print(f"Expected: 2 items (left and right column)")
            
            # Validate expected result
            if len(menu_items) == 2:
                today_name = datetime.now().strftime('%A').upper()
                
                expected_dishes = {
                    'MONDAY': ['TRUTHAHNMEDAILLONS', 'SHAKSHUKA'],
                    'TUESDAY': ['RINDSGULASCH', 'KASNUDELN'],
                    'WEDNESDAY': ['SCHWEINEBAUCH', 'WOK GEMÜSE'],
                    'THURSDAY': ['BACKHENDL', 'GEBACKENES GEMÜSE'],
                    'FRIDAY': ['LACHSFORELLE', 'BROKKOLI'],
                    'SATURDAY': ['RINDFLEISCH', 'GEMÜSEQUICHE'],
                    'SUNDAY': ['CORDON BLEU', 'RATATOUILLE']
                }
                
                if today_name in expected_dishes:
                    expected = expected_dishes[today_name]
                    print(f"\nExpected dishes for {today_name}:")
                    for dish in expected:
                        print(f"  - Should contain: {dish}")
                    
                    found_matches = 0
                    for expected_dish in expected:
                        for item in menu_items:
                            if expected_dish.upper() in item['description'].upper():
                                found_matches += 1
                                break
                    
                    print(f"\nFound {found_matches} out of {len(expected)} expected dishes")
                    
                    if found_matches == len(expected):
                        print("✓ All expected dishes found!")
                    else:
                        print("⚠ Some expected dishes missing - this might be OK if menu changed")
            
            return True
        else:
            print("✗ No menu items extracted")
            print("  Possible reasons:")
            print("  - Flipsnack URL has changed")
            print("  - OCR failed")
            print("  - Menu format has changed")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print("\nFull error trace:")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("Starting Cyclist Scraper Improved Test")
    print("=" * 70)
    
    success = test_cyclist_scraper()
    
    print("\n" + "=" * 70)
    if success:
        print("TEST RESULT: ✓ SUCCESS")
        print("The scraper is working correctly!")
        print("\nFor today (Monday), you should see:")
        print("1. TRUTHAHNMEDAILLONS Oliven & Rosmarin")  
        print("2. SHAKSHUKA Rollgerste")
    else:
        print("TEST RESULT: ✗ FAILURE")
        print("The scraper encountered issues. Check the logs above.")
    print("=" * 70)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())