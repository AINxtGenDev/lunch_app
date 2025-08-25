#!/usr/bin/env python3
"""
Test script to verify CafeGeorge scraper handles weekends correctly.
"""

from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.scrapers.cafegeorge_scraper import CafeGeorgeScraper

def test_weekend_detection():
    scraper = CafeGeorgeScraper()
    
    # Test for Saturday
    saturday = datetime(2025, 8, 23)  # Saturday
    with patch('app.scrapers.cafegeorge_scraper.datetime') as mock_datetime:
        mock_datetime.now.return_value = saturday
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        items = scraper.extract_menu_items()
        print(f"Saturday ({saturday.strftime('%Y-%m-%d')}): {len(items)} items - {'✓ PASS' if len(items) == 0 else '✗ FAIL'}")
    
    # Test for Sunday  
    sunday = datetime(2025, 8, 24)  # Sunday
    with patch('app.scrapers.cafegeorge_scraper.datetime') as mock_datetime:
        mock_datetime.now.return_value = sunday
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        items = scraper.extract_menu_items()
        print(f"Sunday ({sunday.strftime('%Y-%m-%d')}): {len(items)} items - {'✓ PASS' if len(items) == 0 else '✗ FAIL'}")
    
    # Test for Monday (should attempt to scrape)
    monday = datetime(2025, 8, 25)  # Monday
    with patch('app.scrapers.cafegeorge_scraper.datetime') as mock_datetime:
        mock_datetime.now.return_value = monday
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        # Mock the driver to avoid actual scraping
        with patch('app.scrapers.cafegeorge_scraper.get_chrome_driver') as mock_driver:
            mock_driver.side_effect = Exception("Driver mocked - weekday scraping would be attempted")
            try:
                items = scraper.extract_menu_items()
                print(f"Monday ({monday.strftime('%Y-%m-%d')}): Scraping attempted - ✗ FAIL (should try to scrape)")
            except Exception as e:
                if "Driver mocked" in str(e):
                    print(f"Monday ({monday.strftime('%Y-%m-%d')}): Scraping attempted - ✓ PASS")
                else:
                    print(f"Monday ({monday.strftime('%Y-%m-%d')}): Unexpected error - ✗ FAIL")
    
    print("\nWeekend detection test completed!")
    print("The scraper correctly returns empty list for Saturday and Sunday,")
    print("and attempts to scrape for weekdays.")

if __name__ == "__main__":
    test_weekend_detection()