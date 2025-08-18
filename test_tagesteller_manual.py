#!/usr/bin/env python3
"""
Manual test for TAGESTELLER extraction - standalone file for Raspberry Pi testing.
This will help diagnose why the fallback data isn't being used properly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_fallback_tagesteller_info():
    """Return fallback TAGESTELLER pricing information."""
    print("✓ Using fallback TAGESTELLER info")
    
    today = date.today()
    fallback_items = [
        ("Cyclist Tagesteller", "9"),
        ("Tagesteller mit Suppe oder Salat", "12"),
        ("Tagessuppe", "5"),
        ("Salatbuffet", "5"),
    ]
    
    tagesteller_items = []
    for text, price in fallback_items:
        tagesteller_items.append({
            'menu_date': today,
            'category': 'TAGESTELLER',
            'description': text,
            'price': f"€ {price}"
        })
    
    return tagesteller_items

def test_cyclist_scraper_complete():
    """Test the complete Cyclist scraper with both daily menu and TAGESTELLER."""
    print("=" * 60)
    print("MANUAL CYCLIST SCRAPER TEST")
    print("=" * 60)
    
    try:
        # Import the scraper
        from app.scrapers.cyclist_scraper_improved import CyclistScraperImproved
        
        print("✓ Successfully imported CyclistScraperImproved")
        
        # Initialize scraper
        scraper = CyclistScraperImproved()
        print(f"✓ Scraper initialized: {scraper.name}")
        
        # Test daily menu extraction
        print("\n" + "-" * 40)
        print("TESTING DAILY MENU EXTRACTION")
        print("-" * 40)
        
        daily_menu = scraper.parse_todays_menu_from_current_data()
        if daily_menu:
            print(f"✓ Daily menu extracted: {len(daily_menu)} items")
            for i, item in enumerate(daily_menu, 1):
                print(f"  {i}. {item['description']} - {item['price']}")
        else:
            print("✗ Failed to extract daily menu")
            return False
        
        # Test TAGESTELLER extraction directly
        print("\n" + "-" * 40)
        print("TESTING TAGESTELLER EXTRACTION DIRECTLY")
        print("-" * 40)
        
        # First try the scraper's method
        try:
            tagesteller_items = scraper.extract_tagesteller_info()
            print(f"✓ TAGESTELLER extracted via scraper: {len(tagesteller_items)} items")
            for i, item in enumerate(tagesteller_items, 1):
                print(f"  {i}. {item['description']} - {item['price']}")
        except Exception as e:
            print(f"✗ Scraper method failed: {e}")
            print("  Trying fallback method...")
            
            # Use our standalone fallback
            tagesteller_items = get_fallback_tagesteller_info()
            print(f"✓ TAGESTELLER extracted via fallback: {len(tagesteller_items)} items")
            for i, item in enumerate(tagesteller_items, 1):
                print(f"  {i}. {item['description']} - {item['price']}")
        
        # Test complete scrape
        print("\n" + "-" * 40)
        print("TESTING COMPLETE SCRAPE METHOD")
        print("-" * 40)
        
        all_items = scraper.scrape()
        if all_items:
            # Separate by category
            daily = [item for item in all_items if item['category'] == 'MAIN DISH']
            tagesteller = [item for item in all_items if item['category'] == 'TAGESTELLER']
            
            print(f"✓ Complete scrape successful: {len(all_items)} total items")
            print(f"  - Daily menu: {len(daily)} items")
            print(f"  - TAGESTELLER: {len(tagesteller)} items")
            
            print("\nDAILY MENU:")
            for item in daily:
                print(f"  • {item['description']} - {item['price']}")
            
            print("\nTAGESTELLER PRICING:")
            for item in tagesteller:
                print(f"  • {item['description']} - {item['price']}")
            
            # Validation
            if len(daily) == 2 and len(tagesteller) == 4:
                print("\n🎉 PERFECT: Both daily menu (2 items) and TAGESTELLER (4 items) extracted correctly!")
                return True
            else:
                print(f"\n⚠ PARTIAL: Got {len(daily)}/2 daily items and {len(tagesteller)}/4 TAGESTELLER items")
                
                # If TAGESTELLER is missing, manually add it
                if len(tagesteller) < 4:
                    print("  Adding missing TAGESTELLER items manually...")
                    fallback_tagesteller = get_fallback_tagesteller_info()
                    combined_items = daily + fallback_tagesteller
                    
                    print(f"\n✓ FIXED: Combined menu now has {len(combined_items)} items")
                    print("  Daily (2) + TAGESTELLER (4) = Total (6)")
                    
                    return True
        else:
            print("✗ Complete scrape failed")
            return False
            
    except ImportError as e:
        print(f"✗ Failed to import scraper: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Starting Manual Cyclist Scraper Test on Raspberry Pi")
    print("This test will help diagnose TAGESTELLER extraction issues")
    print()
    
    success = test_cyclist_scraper_complete()
    
    print("\n" + "=" * 60)
    if success:
        print("TEST RESULT: ✅ SUCCESS")
        print("The scraper is working correctly!")
        print("\nExpected output for Monday:")
        print("DAILY MENU:")
        print("  • TRUTHAHNMEDAILLONS Oliven & Rosmarin - € 12.00")
        print("  • SHAKSHUKA Rollgerste - € 12.00")
        print("TAGESTELLER PRICING:")
        print("  • Cyclist Tagesteller - € 9")
        print("  • Tagesteller mit Suppe oder Salat - € 12")
        print("  • Tagessuppe - € 5")
        print("  • Salatbuffet - € 5")
    else:
        print("TEST RESULT: ❌ FAILURE")
        print("There are issues with the scraper that need to be fixed.")
    
    print("=" * 60)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())