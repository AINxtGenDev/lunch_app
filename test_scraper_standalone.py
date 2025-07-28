# test_scraper_standalone.py
#!/usr/bin/env python3
"""
Standalone test for the Erste Campus scraper without Flask dependencies.
"""
import os
import sys
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional

# Add project to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


class SimpleErsteCampusScraper:
    """Simplified scraper for testing without database dependencies."""
    
    def __init__(self):
        self.name = "Erste Campus"
        self.api_endpoints = [
            "https://www.gourmet.at/rest-api/menu/EAT-01011001",
            "https://erstecampus.at/wp-json/ec/v1/menu",
        ]
        
    def scrape(self) -> Optional[List[Dict]]:
        """Test the scraping functionality."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for api_url in self.api_endpoints:
            print(f"\n🔍 Trying API: {api_url}")
            
            try:
                response = requests.get(api_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                print(f"✅ Got response from {api_url}")
                
                # Parse based on response type
                if isinstance(data, list):
                    return self._parse_gourmet_api(data)
                elif isinstance(data, dict):
                    return self._parse_erste_api(data)
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed: {e}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode failed: {e}")
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                
        return None
        
    def _parse_gourmet_api(self, data: List[Dict]) -> List[Dict]:
        """Parse GOURMET API format."""
        menu_items = []
        
        for day_data in data:
            menu_date_str = day_data.get("date")
            if not menu_date_str:
                continue
                
            try:
                menu_date = datetime.strptime(menu_date_str, "%Y-%m-%d").date()
            except ValueError:
                continue
                
            for item in day_data.get("menus", []):
                description = item.get("description", "")
                # Remove HTML tags
                import re
                description = re.sub(r'<[^>]+>', '', description)
                description = re.sub(r'\s+', ' ', description).strip()
                
                price_data = item.get("price", {})
                price = ""
                if isinstance(price_data, dict):
                    price_val = price_data.get("price", "")
                    if price_val and price_val != "N/A":
                        price = f"€ {price_val}"
                
                if description:
                    menu_items.append({
                        "menu_date": menu_date,
                        "category": item.get("title", "Main Dish").strip(),
                        "description": description,
                        "price": price
                    })
                    
        return menu_items
        
    def _parse_erste_api(self, data: Dict) -> List[Dict]:
        """Parse Erste Campus API format."""
        menu_items = []
        
        for day_name, day_menu in data.items():
            if not isinstance(day_menu, dict):
                continue
                
            menu_date_str = day_menu.get("date")
            if not menu_date_str:
                continue
                
            try:
                menu_date = datetime.strptime(menu_date_str, "%Y-%m-%d").date()
            except ValueError:
                continue
                
            for item in day_menu.get("menu", []):
                description = item.get("description", "")
                import re
                description = re.sub(r'\s+', ' ', description).strip()
                
                if description:
                    menu_items.append({
                        "menu_date": menu_date,
                        "category": item.get("title", "Main Dish").strip(),
                        "description": description,
                        "price": ""
                    })
                    
        return menu_items


def main():
    """Run the standalone test."""
    print("🍽️  Testing Erste Campus Scraper")
    print("=" * 60)
    
    scraper = SimpleErsteCampusScraper()
    results = scraper.scrape()
    
    if results:
        print(f"\n✅ Successfully scraped {len(results)} menu items!")
        print("\n📋 Sample menu items:")
        print("-" * 60)
        
        for i, item in enumerate(results[:5], 1):
            print(f"\nItem {i}:")
            print(f"  📅 Date: {item['menu_date']}")
            print(f"  🏷️  Category: {item['category']}")
            print(f"  📝 Description: {item['description']}")
            print(f"  💰 Price: {item['price'] or 'N/A'}")
            
        if len(results) > 5:
            print(f"\n... and {len(results) - 5} more items")
    else:
        print("\n❌ No results found!")
        print("\nPossible issues:")
        print("  - API endpoints may have changed")
        print("  - Network connectivity issues")
        print("  - API may require authentication")


if __name__ == "__main__":
    main()
