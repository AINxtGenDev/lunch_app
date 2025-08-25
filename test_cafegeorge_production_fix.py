#!/usr/bin/env python3
"""
Test to verify CafeGeorge scraper correctly handles weekends vs weekdays.
This addresses the production issue where menu was shown on weekends.
"""

from datetime import datetime, timedelta
from unittest.mock import patch
import sys

# Add the app directory to the path
sys.path.insert(0, '/home/nuc8/tmp/lunch_app')

from app.scrapers.cafegeorge_scraper import CafeGeorgeScraper

def test_all_days():
    """Test scraper behavior for each day of the week."""
    scraper = CafeGeorgeScraper()
    
    # Start from a known Monday
    base_date = datetime(2025, 8, 25)  # Monday, August 25, 2025
    
    print("Testing CafeGeorge scraper for all days of the week:")
    print("=" * 60)
    
    for days_offset in range(7):
        test_date = base_date + timedelta(days=days_offset)
        day_name = test_date.strftime("%A")
        
        with patch('app.scrapers.cafegeorge_scraper.datetime') as mock_datetime:
            # Configure the mock to return our test date
            mock_datetime.now.return_value = test_date
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            try:
                items = scraper.extract_menu_items()
                
                # Expected behavior:
                # Mon-Fri (0-4): Should attempt to scrape (would fail without browser)
                # Sat-Sun (5-6): Should return empty list immediately
                
                weekday_num = test_date.weekday()
                is_weekend = weekday_num >= 5
                
                if is_weekend:
                    if len(items) == 0:
                        status = "✓ PASS - Returns empty (no menu on weekends)"
                    else:
                        status = f"✗ FAIL - Returned {len(items)} items (should be 0)"
                else:
                    # On weekdays, it should try to scrape (will fail without browser)
                    status = "✗ FAIL - Did not attempt scraping"
                    
            except Exception as e:
                # On weekdays, we expect failure due to no browser in test
                weekday_num = test_date.weekday()
                is_weekend = weekday_num >= 5
                
                if is_weekend:
                    status = f"✗ FAIL - Error on weekend: {str(e)[:50]}"
                else:
                    if "get_chrome_driver" in str(e) or "driver" in str(e).lower():
                        status = "✓ PASS - Attempts to scrape (browser init)"
                    else:
                        status = f"? UNKNOWN - {str(e)[:50]}"
            
            print(f"{day_name:9} ({test_date.strftime('%Y-%m-%d')}): {status}")
    
    print("=" * 60)
    print("\nSummary:")
    print("- Monday-Friday: Scraper attempts to fetch menu (needs browser)")
    print("- Saturday-Sunday: Returns empty list (no menu available)")
    print("\nThis matches the Cafe George website which shows menu only Mon-Fri")

if __name__ == "__main__":
    # First show current day status
    now = datetime.now()
    print(f"\nCurrent time: {now.strftime('%A, %B %d, %Y at %H:%M')}")
    print(f"Current weekday: {now.weekday()} (0=Monday, 6=Sunday)")
    
    if now.weekday() >= 5:
        print("→ It's the weekend, scraper should return empty list\n")
    else:
        print("→ It's a weekday, scraper should attempt to fetch menu\n")
    
    test_all_days()