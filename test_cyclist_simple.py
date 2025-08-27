#!/usr/bin/env python3
# test_cyclist_simple.py
"""
Simple test script for the production Cyclist scraper without database dependencies.
"""
import sys
import os
import logging
import requests

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_url_discovery():
    """Test URL discovery from the main Cyclist website."""
    print("🔍 Testing URL Discovery from Main Site")
    print("=" * 40)
    
    try:
        from app.scrapers.cyclist_scraper_production import CyclistScraperProduction
        
        # Create scraper without Flask context
        scraper = CyclistScraperProduction()
        
        print("📡 Discovering current menu URLs...")
        discovered_urls = scraper.discover_current_menu_urls()
        
        print(f"✅ Found {len(discovered_urls)} URLs:")
        for i, url in enumerate(discovered_urls, 1):
            print(f"   {i}. {url}")
        
        return len(discovered_urls) > 0
        
    except Exception as e:
        print(f"❌ URL discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_urls():
    """Test intelligent fallback URL generation."""
    print("\n🔄 Testing Fallback URL Generation")
    print("=" * 35)
    
    try:
        from app.scrapers.cyclist_scraper_production import CyclistScraperProduction
        
        scraper = CyclistScraperProduction()
        
        print("🎯 Generating fallback URLs...")
        fallback_urls = scraper.get_intelligent_fallback_urls()
        
        print(f"✅ Generated {len(fallback_urls)} fallback URLs:")
        for i, url in enumerate(fallback_urls[:5], 1):  # Show first 5
            print(f"   {i}. {url}")
        
        return len(fallback_urls) > 0
        
    except Exception as e:
        print(f"❌ Fallback URL generation failed: {e}")
        return False

def test_actual_website():
    """Test actual website response."""
    print("\n🌐 Testing Actual Website Connection")
    print("=" * 35)
    
    try:
        url = "https://www.cafe-cyclist.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        print(f"🎯 Testing connection to: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        print(f"✅ Response: {response.status_code}")
        print(f"📊 Content length: {len(response.content)} bytes")
        
        # Check for Flipsnack links
        content = response.text.lower()
        flipsnack_count = content.count('flipsnack.com')
        print(f"🔗 Flipsnack mentions: {flipsnack_count}")
        
        # Look for specific terms
        terms = ['tagesteller', 'wochenmen', 'menu']
        found_terms = [term for term in terms if term in content]
        print(f"📝 Found terms: {found_terms}")
        
        return response.status_code == 200 and flipsnack_count > 0
        
    except Exception as e:
        print(f"❌ Website connection failed: {e}")
        return False

def test_emergency_fallback():
    """Test emergency fallback menu generation."""
    print("\n🚨 Testing Emergency Fallback Menu")
    print("=" * 33)
    
    try:
        from app.scrapers.cyclist_scraper_production import CyclistScraperProduction
        
        scraper = CyclistScraperProduction()
        
        print("🎯 Generating emergency fallback menu...")
        fallback_menu = scraper.get_emergency_fallback_menu()
        
        print(f"✅ Generated {len(fallback_menu)} menu items:")
        for i, item in enumerate(fallback_menu, 1):
            category = item.get('category', 'N/A')
            description = item.get('description', 'N/A')
            price = item.get('price', 'N/A')
            print(f"   {i}. [{category}] {description}")
            if price and price != 'N/A':
                print(f"      Price: {price}")
        
        return len(fallback_menu) > 0
        
    except Exception as e:
        print(f"❌ Emergency fallback failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🏁 Starting Simple Cyclist Scraper Tests")
    print("=" * 50)
    
    tests = [
        ("URL Discovery", test_url_discovery),
        ("Fallback URLs", test_fallback_urls),
        ("Website Connection", test_actual_website),
        ("Emergency Fallback", test_emergency_fallback),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            success = test_func()
            results.append((test_name, success))
            print(f"{'✅ PASSED' if success else '❌ FAILED'}: {test_name}")
        except Exception as e:
            print(f"💥 CRASHED: {test_name} - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS SUMMARY:")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n🏆 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Production scraper is ready!")
        return True
    else:
        print("⚠️  Some tests failed - review before production deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)