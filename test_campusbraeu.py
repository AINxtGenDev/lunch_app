#!/usr/bin/env python3
"""
Test script for Campus Bräu scraper pricing fix.
This script tests that the lunch menu price (€15.50) is only shown on the main dish,
while soup and dessert have no price (as they're included in the lunch menu).
"""

import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_campusbraeu_scraper():
    """Test the Campus Bräu scraper with focus on pricing."""
    
    try:
        # Import the scraper
        from app.scrapers.campusbraeu_scraper import CampusBrauScraper
        
        logger.info("=" * 60)
        logger.info("Testing Campus Bräu Scraper - Pricing Fix")
        logger.info("=" * 60)
        logger.info(f"Test started at: {datetime.now()}")
        logger.info(f"Expected behavior: Only main dishes should have €15.50 price")
        logger.info(f"Soup and Dessert should have no price (included in menu)")
        logger.info("-" * 60)
        
        # Initialize scraper
        scraper = CampusBrauScraper()
        logger.info(f"Scraper initialized for: {scraper.name}")
        logger.info(f"URL: {scraper.url}")
        
        # Run the scraper
        logger.info("\nStarting scraping process...")
        menu_items = scraper.scrape()
        
        # Analyze results
        logger.info("\n" + "=" * 60)
        logger.info(f"RESULTS: Extracted {len(menu_items)} menu items")
        logger.info("=" * 60)
        
        # Group items by category for analysis
        soups = []
        main_dishes = []
        desserts = []
        
        for item in menu_items:
            category = item.get('category', '').lower()
            if 'soup' in category or 'suppe' in category:
                soups.append(item)
            elif 'main' in category or 'haupt' in category:
                main_dishes.append(item)
            elif 'dessert' in category or 'nach' in category:
                desserts.append(item)
        
        # Display results organized by category
        print("\n" + "=" * 60)
        print("SCRAPED MENU ITEMS BY CATEGORY")
        print("=" * 60)
        
        print(f"\n📍 SOUPS ({len(soups)} items):")
        print("-" * 40)
        for item in soups:
            price = item.get('price', 'No price')
            desc = item['description'][:60] if len(item['description']) > 60 else item['description']
            print(f"  • {desc}")
            print(f"    Price: {price}")
            if price and price != 'No price':
                print(f"    ⚠️  WARNING: Soup has price! Should be 'No price'")
        
        print(f"\n🍽️  MAIN DISHES ({len(main_dishes)} items):")
        print("-" * 40)
        for item in main_dishes:
            price = item.get('price', 'No price')
            desc = item['description'][:60] if len(item['description']) > 60 else item['description']
            print(f"  • {desc}")
            print(f"    Price: {price}")
            if price != "€ 15,50":
                print(f"    ⚠️  WARNING: Main dish should have price €15.50!")
        
        print(f"\n🍰 DESSERTS ({len(desserts)} items):")
        print("-" * 40)
        for item in desserts:
            price = item.get('price', 'No price')
            desc = item['description'][:60] if len(item['description']) > 60 else item['description']
            print(f"  • {desc}")
            print(f"    Price: {price}")
            if price and price != 'No price':
                print(f"    ⚠️  WARNING: Dessert has price! Should be 'No price'")
        
        # Validation summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        errors = []
        
        # Check soups
        soups_with_price = [s for s in soups if s.get('price') and s.get('price') != 'No price']
        if soups_with_price:
            errors.append(f"❌ {len(soups_with_price)} soup(s) have prices (should have none)")
        else:
            print("✅ All soups have no price (correct)")
        
        # Check main dishes
        mains_without_correct_price = [m for m in main_dishes if m.get('price') != "€ 15,50"]
        if mains_without_correct_price:
            errors.append(f"❌ {len(mains_without_correct_price)} main dish(es) don't have €15.50 price")
        else:
            print("✅ All main dishes have €15.50 price (correct)")
        
        # Check desserts
        desserts_with_price = [d for d in desserts if d.get('price') and d.get('price') != 'No price']
        if desserts_with_price:
            errors.append(f"❌ {len(desserts_with_price)} dessert(s) have prices (should have none)")
        else:
            print("✅ All desserts have no price (correct)")
        
        # Final result
        print("\n" + "=" * 60)
        if errors:
            print("TEST FAILED ❌")
            print("Issues found:")
            for error in errors:
                print(f"  {error}")
        else:
            print("TEST PASSED ✅")
            print("All items have correct pricing:")
            print("  • Soups: No price (included in menu)")
            print("  • Main dishes: €15.50 (lunch menu price)")
            print("  • Desserts: No price (included in menu)")
        print("=" * 60)
        
        return len(errors) == 0
        
    except Exception as e:
        logger.error(f"Error during test: {str(e)}", exc_info=True)
        print(f"\n❌ TEST FAILED WITH ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_campusbraeu_scraper()
    sys.exit(0 if success else 1)