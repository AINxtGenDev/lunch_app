#!/usr/bin/env python3
"""Test that daily menu items no longer have prices (since pricing is in TAGESTELLER)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.cyclist_scraper_improved import CyclistScraperImproved

def main():
    print("Testing Cyclist Scraper - Price Removal Check")
    print("=" * 60)
    
    scraper = CyclistScraperImproved()
    menu_items = scraper.scrape()
    
    if menu_items:
        # Separate by category
        daily_menu = [item for item in menu_items if item['category'] == 'MAIN DISH']
        tagesteller_info = [item for item in menu_items if item['category'] == 'TAGESTELLER']
        
        print(f"Total items: {len(menu_items)}")
        print(f"Daily menu: {len(daily_menu)} items")
        print(f"TAGESTELLER: {len(tagesteller_info)} items")
        
        print("\nDAILY MENU (no prices - see TAGESTELLER for pricing):")
        for item in daily_menu:
            price_display = item['price'] if item['price'] else "(no price shown)"
            print(f"  • {item['description']} - {price_display}")
        
        print("\nTAGESTELLER PRICING (actual prices):")
        for item in tagesteller_info:
            print(f"  • {item['description']} - {item['price']}")
        
        # Validation
        print("\n" + "=" * 60)
        print("VALIDATION:")
        
        # Check that daily menu items have no price
        daily_with_price = [item for item in daily_menu if item['price'] and item['price'] != '']
        if daily_with_price:
            print(f"❌ ERROR: {len(daily_with_price)} daily menu items still have prices!")
            for item in daily_with_price:
                print(f"   - {item['description']}: {item['price']}")
        else:
            print("✅ SUCCESS: Daily menu items have no prices (as intended)")
        
        # Check that TAGESTELLER items have prices
        tagesteller_without_price = [item for item in tagesteller_info if not item['price'] or item['price'] == '']
        if tagesteller_without_price:
            print(f"❌ ERROR: {len(tagesteller_without_price)} TAGESTELLER items missing prices!")
            for item in tagesteller_without_price:
                print(f"   - {item['description']}")
        else:
            print("✅ SUCCESS: All TAGESTELLER items have prices")
        
        print("=" * 60)
        print("\nEXPLANATION:")
        print("Daily dishes show no price because customers choose from:")
        print("  • Cyclist Tagesteller - € 9 (dish only)")
        print("  • Tagesteller mit Suppe oder Salat - € 12 (with soup/salad)")
        print("This avoids confusion from showing a fixed € 12.00 price.")
        
    else:
        print("❌ FAILED: No menu items found")

if __name__ == "__main__":
    main()