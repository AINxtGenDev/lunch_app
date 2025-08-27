#!/usr/bin/env python3
# test_cyclist_fix.py
"""
Quick test to verify the enhanced Cyclist scraper fixes.
"""
import sys
import os
import logging

# Add the app directory to Python path  
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_enhanced_scraper():
    """Test the enhanced OCR parsing."""
    print("🔧 Testing Enhanced Cyclist Scraper")
    print("=" * 40)
    
    try:
        from app.scrapers.cyclist_scraper_production import CyclistScraperProduction
        
        scraper = CyclistScraperProduction()
        
        # Test with sample OCR text that might contain the actual menu items
        sample_ocr_text = """
        MITTWOCH
        HÄHNCHENSPIESSE Honig & Zitrone
        RAVIOLI Tomatensauce
        
        DONNERSTAG  
        Other items here
        """
        
        print("🧪 Testing OCR text parsing...")
        menu_items = scraper.parse_ocr_text_to_menu_items(sample_ocr_text)
        
        print(f"✅ Parsed {len(menu_items)} items:")
        for i, item in enumerate(menu_items, 1):
            print(f"   {i}. {item['description']}")
        
        # Test fallback URL generation
        print("\n🔄 Testing enhanced fallback URLs...")
        fallback_urls = scraper.get_intelligent_fallback_urls()
        
        print(f"✅ Generated {len(fallback_urls)} URLs:")
        for i, url in enumerate(fallback_urls[:5], 1):  # Show first 5
            print(f"   {i}. {url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_scraper()
    sys.exit(0 if success else 1)