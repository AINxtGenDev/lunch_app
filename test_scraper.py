# test_scraper.py
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Ensure instance directory exists
instance_dir = os.path.join(os.path.dirname(__file__), "instance")
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir, exist_ok=True)

from app import create_app
from app.scrapers.erste_campus_scraper import ErsteCampusScraper

# Create the app
app = create_app("development")

with app.app_context():
    print("Testing Erste Campus Scraper...")
    scraper = ErsteCampusScraper()

    try:
        results = scraper.scrape()

        if results:
            print(f"\n✅ Successfully scraped {len(results)} menu items:")
            print("=" * 60)
            for i, item in enumerate(results[:5], 1):  # Show first 5 items
                print(f"\nItem {i}:")
                print(f"  Date: {item['menu_date']}")
                print(f"  Category: {item['category']}")
                print(f"  Description: {item['description']}")
                print(f"  Price: {item['price']}")

            if len(results) > 5:
                print(f"\n... and {len(results) - 5} more items")
        else:
            print("\n❌ Scraping returned no results!")

    except Exception as e:
        print(f"\n❌ Scraping failed with error: {e}")
        import traceback

        traceback.print_exc()
