#!/usr/bin/env python3
"""
Test script for Albanco scraper.
Run this to manually test the Albanco restaurant menu scraper.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.albanco_scraper import AlbancoScraper
import logging
from datetime import datetime

# Set up logging with detailed output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_albanco_scraper():
    """Test the Albanco scraper functionality."""
    print("=" * 70)
    print("ALBANCO SCRAPER TEST")
    print("=" * 70)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    
    try:
        # Initialize scraper
        scraper = AlbancoScraper()
        print(f"\n✓ Scraper initialized: {scraper.name}")
        print(f"  Base URL: {scraper.url}")
        
        # Test 1: Find PDF URL
        print("\n" + "=" * 70)
        print("TEST 1: PDF URL Discovery")
        print("-" * 70)
        
        pdf_url = scraper.find_current_weekly_pdf_url()
        if pdf_url:
            print(f"✓ PDF URL found successfully")
            print(f"  URL: {pdf_url}")
        else:
            print("✗ Failed to find PDF URL")
            print("  The website might have changed or the PDF is not available")
            return False
        
        # Test 2: Extract menu items
        print("\n" + "=" * 70)
        print("TEST 2: Menu Extraction")
        print("-" * 70)
        
        menu_items = scraper.extract_menu_items()
        
        if menu_items:
            print(f"✓ Successfully extracted {len(menu_items)} menu items")
            
            # Display menu items by category
            print("\n" + "=" * 70)
            print("EXTRACTED MENU ITEMS")
            print("-" * 70)
            
            # Group items by category
            categories = {}
            for item in menu_items:
                category = item.get('category', 'UNCATEGORIZED')
                if category not in categories:
                    categories[category] = []
                categories[category].append(item)
            
            # Display by category
            for category in sorted(categories.keys()):
                print(f"\n{category}:")
                print("-" * 40)
                for item in categories[category]:
                    print(f"  • {item['description']}")
                    print(f"    Price: {item['price']}")
                    print(f"    Date: {item['menu_date']}")
                    print()
            
            # Summary statistics
            print("\n" + "=" * 70)
            print("SUMMARY")
            print("-" * 70)
            print(f"Total items: {len(menu_items)}")
            print(f"Categories: {', '.join(sorted(categories.keys()))}")
            for category, items in categories.items():
                print(f"  - {category}: {len(items)} items")
            
            return True
        else:
            print("✗ No menu items extracted")
            print("  Possible reasons:")
            print("  - PDF format has changed")
            print("  - PDF is empty or corrupted")
            print("  - Parser needs updating")
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
    print("Starting Albanco Scraper Test")
    print("=" * 70)
    
    success = test_albanco_scraper()
    
    print("\n" + "=" * 70)
    if success:
        print("TEST RESULT: ✓ SUCCESS")
        print("The scraper is working correctly!")
    else:
        print("TEST RESULT: ✗ FAILURE")
        print("The scraper encountered issues. Check the logs above.")
    print("=" * 70)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())