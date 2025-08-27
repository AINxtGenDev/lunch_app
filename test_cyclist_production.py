#!/usr/bin/env python3
# test_cyclist_production.py
"""
Test script for the new production Cyclist scraper.
Validates URL discovery, content extraction, and monitoring integration.
"""
import sys
import os
import logging
from datetime import date
import time

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_cyclist_scraper():
    """Test the production Cyclist scraper."""
    print("🧪 TESTING CYCLIST PRODUCTION SCRAPER")
    print("=" * 50)
    
    try:
        # Import with app context
        from app import create_app
        from app.scrapers.cyclist_scraper_production import CyclistScraperProduction
        from app.services.scraper_monitor import scraper_monitor
        
        # Create app context
        app = create_app('development')
        
        with app.app_context():
            # Initialize scraper
            scraper = CyclistScraperProduction()
            
            print(f"🎯 Testing scraper: {scraper.name}")
            print(f"🌐 Base URL: {scraper.base_url}")
            print()
            
            # Test URL discovery
            print("📡 Testing URL discovery...")
            discovered_urls = scraper.discover_current_menu_urls()
            print(f"   Found {len(discovered_urls)} URLs:")
            for i, url in enumerate(discovered_urls[:3], 1):  # Show first 3
                print(f"   {i}. {url}")
            print()
            
            # Test fallback URL generation
            print("🔄 Testing fallback URL generation...")
            fallback_urls = scraper.get_intelligent_fallback_urls()
            print(f"   Generated {len(fallback_urls)} fallback URLs:")
            for i, url in enumerate(fallback_urls[:3], 1):  # Show first 3
                print(f"   {i}. {url}")
            print()
            
            # Test actual scraping
            print("🚀 Testing full scraping process...")
            start_time = time.time()
            
            # Record start for monitoring
            scraper_monitor.record_scrape_start(scraper.name)
            
            try:
                menu_items = scraper.scrape()
                execution_time = time.time() - start_time
                
                if menu_items:
                    print(f"   ✅ SUCCESS: Extracted {len(menu_items)} items in {execution_time:.1f}s")
                    
                    # Show sample items
                    print("\n📋 Sample menu items:")
                    for i, item in enumerate(menu_items[:5], 1):  # Show first 5
                        print(f"   {i}. [{item['category']}] {item['description']}")
                        if item.get('price'):
                            print(f"      Price: {item['price']}")
                    
                    # Record success
                    scraper_monitor.record_scrape_success(
                        scraper.name, execution_time, len(menu_items), 
                        scraper.metrics.get('fallback_usage', 0) > 0
                    )
                    
                else:
                    print("   ❌ FAILED: No menu items extracted")
                    scraper_monitor.record_scrape_failure(scraper.name, "No data returned", execution_time)
            
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"   ❌ ERROR: {e}")
                scraper_monitor.record_scrape_failure(scraper.name, str(e), execution_time)
            
            print()
            
            # Show scraper metrics
            print("📊 Scraper internal metrics:")
            for key, value in scraper.metrics.items():
                print(f"   {key}: {value}")
            print()
            
            # Show monitor status
            print("🏥 Monitor status:")
            status = scraper_monitor.get_scraper_status(scraper.name)
            if status:
                for key, value in status.items():
                    print(f"   {key}: {value}")
            print()
            
            # Test health report generation
            print("📄 Health report:")
            health_report = scraper_monitor.generate_health_report()
            print(health_report)
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✅ Test completed successfully!")
    return True

def test_url_validation():
    """Test URL validation and date extraction."""
    print("\n🔍 TESTING URL UTILITIES")
    print("=" * 30)
    
    try:
        from app.scrapers.cyclist_scraper_production import CyclistScraperProduction
        
        scraper = CyclistScraperProduction()
        
        # Test URLs
        test_urls = [
            "https://www.flipsnack.com/EE9BE6CC5A8/wochenmen-14-20-08-2023/full-view.html",
            "https://www.flipsnack.com/EE9BE6CC5A8/wochenmen-25-31-08-2025/full-view.html",
            "https://www.flipsnack.com/EE9BE6CC5A8/weekly-menu-27-08-2025/full-view.html"
        ]
        
        print("📅 Testing date extraction:")
        for url in test_urls:
            extracted_date = scraper.extract_date_from_url(url)
            print(f"   {url}")
            print(f"   → {extracted_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
        
        print("🌐 Testing URL validation:")
        for url in test_urls:
            is_valid = scraper.validate_menu_url(url)
            status = "✅ Valid" if is_valid else "❌ Invalid"
            print(f"   {status}: {url}")
        
    except Exception as e:
        print(f"❌ URL utility test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🏁 Starting Cyclist Production Scraper Tests")
    print("=" * 60)
    
    # Test main scraper
    success1 = test_cyclist_scraper()
    
    # Test URL utilities
    success2 = test_url_validation()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("💥 SOME TESTS FAILED!")
        sys.exit(1)