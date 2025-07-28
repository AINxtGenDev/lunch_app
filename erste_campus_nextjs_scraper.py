# erste_campus_nextjs_scraper.py
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import locale

class ErsteCampusNextJSScraper:
    """Scraper for Erste Campus menu using Next.js data extraction."""
    
    def __init__(self):
        self.name = "Erste Campus"
        self.iframe_url = "https://erstecampus.at/mealplan/2025/external/single/kantine-en.html"
        # Try different locale settings for date parsing
        try:
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'C')
            except:
                pass
    
    def scrape(self) -> Optional[List[Dict]]:
        """Main scraping method."""
        print(f"\n🍽️ Scraping {self.name} (Next.js)")
        print("=" * 60)
        
        try:
            # Fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(self.iframe_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the __NEXT_DATA__ script tag
            next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})
            if not next_data_script:
                print("❌ No __NEXT_DATA__ script found")
                return self._fallback_scraping(soup)
            
            # Parse the JSON
            try:
                next_data = json.loads(next_data_script.string)
                print("✅ Found and parsed __NEXT_DATA__")
                
                # Extract menu data
                menu_items = self._extract_menu_from_next_data(next_data)
                
                if menu_items:
                    print(f"✅ Extracted {len(menu_items)} menu items")
                    return menu_items
                else:
                    print("⚠️ No menu items found in Next.js data")
                    # Try to find API endpoint
                    return self._try_api_endpoints(next_data)
                    
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON: {e}")
                return self._fallback_scraping(soup)
                
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_menu_from_next_data(self, data: Dict) -> List[Dict]:
        """Extract menu items from Next.js data structure."""
        menu_items = []
        
        # Navigate through the data structure
        try:
            # Common paths in Next.js apps
            paths_to_try = [
                ['props', 'pageProps', 'menu'],
                ['props', 'pageProps', 'data'],
                ['props', 'pageProps', 'meals'],
                ['props', 'pageProps', 'weeklyMenu'],
                ['props', 'pageProps', 'restaurant', 'menu'],
                ['props', 'pageProps', 'initialData'],
            ]
            
            for path in paths_to_try:
                current = data
                for key in path:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        break
                else:
                    # Successfully navigated the path
                    print(f"  📍 Found data at path: {' -> '.join(path)}")
                    
                    # Try to extract menu items from current
                    if isinstance(current, list):
                        for item in current:
                            extracted = self._parse_menu_item(item)
                            if extracted:
                                menu_items.extend(extracted)
                    elif isinstance(current, dict):
                        extracted = self._parse_menu_structure(current)
                        if extracted:
                            menu_items.extend(extracted)
                            
            # Also check for any embedded data
            self._search_for_menu_data(data, menu_items)
            
        except Exception as e:
            print(f"  ⚠️ Error extracting menu: {e}")
            
        return menu_items
    
    def _search_for_menu_data(self, obj, menu_items: List[Dict], depth: int = 0):
        """Recursively search for menu data in the object."""
        if depth > 10:  # Prevent infinite recursion
            return
            
        if isinstance(obj, dict):
            # Check if this looks like a menu item
            if all(key in obj for key in ['date', 'description']) or \
               all(key in obj for key in ['day', 'menu']) or \
               'meals' in obj:
                extracted = self._parse_menu_structure(obj)
                if extracted:
                    menu_items.extend(extracted)
                    
            # Recurse through dictionary
            for key, value in obj.items():
                if key not in ['_app', '__N_SSG', 'buildId']:  # Skip Next.js internals
                    self._search_for_menu_data(value, menu_items, depth + 1)
                    
        elif isinstance(obj, list):
            for item in obj:
                self._search_for_menu_data(item, menu_items, depth + 1)
    
    def _parse_menu_structure(self, data: Dict) -> List[Dict]:
        """Parse various menu data structures."""
        menu_items = []
        
        # Structure 1: Weekly menu with days
        if 'monday' in data or 'Monday' in data or 'mon' in data:
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in days:
                for key in [day, day.capitalize(), day[:3]]:
                    if key in data:
                        day_data = data[key]
                        menu_date = self._get_date_for_weekday(day)
                        items = self._extract_items_from_day_data(day_data, menu_date)
                        menu_items.extend(items)
                        
        # Structure 2: Array of days
        elif 'days' in data and isinstance(data['days'], list):
            for day_data in data['days']:
                items = self._parse_day_data(day_data)
                menu_items.extend(items)
                
        # Structure 3: Direct menu items
        elif 'items' in data or 'meals' in data or 'menu' in data:
            key = 'items' if 'items' in data else ('meals' if 'meals' in data else 'menu')
            if isinstance(data[key], list):
                for item in data[key]:
                    parsed = self._parse_menu_item(item)
                    if parsed:
                        menu_items.extend(parsed)
                        
        return menu_items
    
    def _parse_day_data(self, day_data: Dict) -> List[Dict]:
        """Parse data for a single day."""
        menu_items = []
        
        # Extract date
        menu_date = None
        if 'date' in day_data:
            menu_date = self._parse_date(day_data['date'])
        elif 'day' in day_data:
            menu_date = self._get_date_for_weekday(day_data['day'])
            
        if not menu_date:
            menu_date = date.today()
            
        # Extract items
        items_key = None
        for key in ['items', 'meals', 'menu', 'dishes']:
            if key in day_data:
                items_key = key
                break
                
        if items_key and isinstance(day_data[items_key], list):
            for item in day_data[items_key]:
                if isinstance(item, dict):
                    parsed = self._parse_single_menu_item(item, menu_date)
                    if parsed:
                        menu_items.append(parsed)
                elif isinstance(item, str) and len(item) > 10:
                    menu_items.append({
                        'menu_date': menu_date,
                        'category': 'Main Dish',
                        'description': item.strip(),
                        'price': ''
                    })
                    
        return menu_items
    
    def _parse_single_menu_item(self, item: Dict, menu_date: date) -> Optional[Dict]:
        """Parse a single menu item."""
        description = None
        
        # Try different keys for description
        for key in ['description', 'name', 'title', 'meal', 'dish', 'text']:
            if key in item:
                description = str(item[key]).strip()
                break
                
        if not description or len(description) < 5:
            return None
            
        # Extract category
        category = 'Main Dish'
        for key in ['category', 'type', 'mealType']:
            if key in item:
                category = str(item[key]).strip()
                break
                
        # Extract price
        price = ''
        for key in ['price', 'cost', 'preis']:
            if key in item:
                price_val = item[key]
                if isinstance(price_val, (int, float)):
                    price = f"€ {price_val:.2f}"
                elif isinstance(price_val, str):
                    price = self._extract_price(price_val)
                break
                    
        return {
            'menu_date': menu_date,
            'category': category,
            'description': self._clean_description(description),
            'price': price
        }
    
    def _parse_menu_item(self, item) -> List[Dict]:
        """Parse various menu item formats."""
        menu_items = []
        
        if isinstance(item, dict):
            # Check if it's a day structure
            if 'date' in item or 'day' in item:
                return self._parse_day_data(item)
            # Single menu item
            else:
                parsed = self._parse_single_menu_item(item, date.today())
                if parsed:
                    menu_items.append(parsed)
                    
        elif isinstance(item, str) and len(item) > 10:
            # Plain text menu item
            menu_items.append({
                'menu_date': date.today(),
                'category': self._determine_category(item),
                'description': self._clean_description(item),
                'price': self._extract_price(item)
            })
            
        return menu_items
    
    def _extract_items_from_day_data(self, day_data, menu_date: date) -> List[Dict]:
        """Extract menu items from day data."""
        menu_items = []
        
        if isinstance(day_data, list):
            for item in day_data:
                if isinstance(item, str) and len(item) > 10:
                    menu_items.append({
                        'menu_date': menu_date,
                        'category': self._determine_category(item),
                        'description': self._clean_description(item),
                        'price': self._extract_price(item)
                    })
                elif isinstance(item, dict):
                    parsed = self._parse_single_menu_item(item, menu_date)
                    if parsed:
                        menu_items.append(parsed)
                        
        elif isinstance(day_data, dict):
            for key, value in day_data.items():
                if isinstance(value, list):
                    for item in value:
                        parsed = self._parse_single_menu_item({'description': item}, menu_date)
                        if parsed:
                            menu_items.append(parsed)
                            
        return menu_items
    
    def _try_api_endpoints(self, next_data: Dict) -> Optional[List[Dict]]:
        """Try to find and call API endpoints from Next.js data."""
        print("\n🔍 Looking for API endpoints...")
        
        # Extract build ID and other info
        build_id = next_data.get('buildId', '')
        restaurant_slug = next_data.get('query', {}).get('slug', 'kantine-en')
        
        # Common Next.js API patterns
        api_patterns = [
            f"https://erstecampus.at/mealplan/2025/_next/data/{build_id}/external/single/{restaurant_slug}.json",
            f"https://erstecampus.at/mealplan/2025/api/menu/{restaurant_slug}",
            f"https://erstecampus.at/mealplan/2025/api/meals",
            "https://erstecampus.at/mealplan/2025/api/weekly-menu",
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': self.iframe_url,
        }
        
        for api_url in api_patterns:
            print(f"  🔗 Trying: {api_url}")
            try:
                response = requests.get(api_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ Success! Got data from API")
                    
                    # Try to extract menu from API response
                    menu_items = self._extract_menu_from_next_data(data)
                    if menu_items:
                        return menu_items
                        
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                continue
                
        return None
    
    def _fallback_scraping(self, soup: BeautifulSoup) -> List[Dict]:
        """Fallback to HTML scraping if JSON extraction fails."""
        print("\n🔄 Trying fallback HTML scraping...")
        
        menu_items = []
        
        # Look for any text that might be menu items
        all_text = soup.get_text()
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        
        current_date = date.today()
        
        for line in lines:
            # Skip short lines, dates, and headers
            if (len(line) > 20 and 
                not self._is_date_text(line) and
                'Uhr' not in line and
                'menu' not in line.lower()):
                
                # Check if it looks like a menu item
                if any(keyword in line.lower() for keyword in ['suppe', 'salat', 'dessert', 'soup', 'salad']):
                    menu_items.append({
                        'menu_date': current_date,
                        'category': self._determine_category(line),
                        'description': self._clean_description(line),
                        'price': self._extract_price(line)
                    })
                    
        return menu_items
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse various date formats."""
        if not date_str:
            return None
            
        # Standard formats
        formats = [
            '%Y-%m-%d',
            '%d.%m.%Y',
            '%d/%m/%Y',
            '%B %d, %Y',
            '%d %B %Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
                
        # ISO format
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        except:
            pass
            
        return None
    
    def _get_date_for_weekday(self, weekday: str) -> date:
        """Get the date for a given weekday in the current week."""
        weekday = weekday.lower()
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        if weekday in days:
            today = date.today()
            current_weekday = today.weekday()
            target_weekday = days.index(weekday)
            
            # Calculate days difference
            days_diff = target_weekday - current_weekday
            
            # Get the date
            target_date = today + timedelta(days=days_diff)
            return target_date
            
        return date.today()
    
    def _is_date_text(self, text: str) -> bool:
        """Check if text is a date."""
        date_patterns = [
            r'\d{1,2}[.\s/]+\d{1,2}[.\s/]+\d{4}',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'(monday|tuesday|wednesday|thursday|friday)',
            r'(montag|dienstag|mittwoch|donnerstag|freitag)',
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in date_patterns)
    
    def _determine_category(self, text: str) -> str:
        """Determine meal category."""
        text_lower = text.lower()
        
        categories = {
            'Soup': ['suppe', 'soup'],
            'Salad': ['salat', 'salad'],
            'Vegetarian': ['vegetarisch', 'vegetarian', 'vegan'],
            'Dessert': ['dessert', 'sweet', 'kuchen', 'obst'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
                
        return 'Main Dish'
    
    def _clean_description(self, text: str) -> str:
        """Clean menu description."""
        # Remove common patterns
        text = re.sub(r'Menü:\s*', '', text)
        text = re.sub(r'€\s*\d+[,.]?\d*', '', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Fix encoding issues
        text = text.replace('Ã¼', 'ü').replace('Ã¶', 'ö').replace('Ã¤', 'ä')
        text = text.replace('ÃŸ', 'ß').replace('Ã©', 'é')
        
        return text.strip()
    
    def _extract_price(self, text: str) -> str:
        """Extract price from text."""
        price_match = re.search(r'€\s*(\d+[,.]?\d*)', text)
        if price_match:
            return f"€ {price_match.group(1)}"
        return ""


if __name__ == "__main__":
    # First examine the JSON structure
    print("📋 Examining extracted JSON data...")
    import examine_menu_json
    examine_menu_json.examine_json_structure()
    
    print("\n" + "=" * 60 + "\n")
    
    # Then run the scraper
    scraper = ErsteCampusNextJSScraper()
    results = scraper.scrape()
    
    if results:
        print(f"\n\n✅ Successfully scraped {len(results)} menu items!")
        
        # Group by date
        from collections import defaultdict
        by_date = defaultdict(list)
        for item in results:
            by_date[item['menu_date']].append(item)
        
        print(f"\n📅 Menu for {len(by_date)} days:")
        for menu_date in sorted(by_date.keys()):
            items = by_date[menu_date]
            print(f"\n📆 {menu_date.strftime('%A, %d %B %Y')}:")
            for item in items:
                print(f"  • [{item['category']}] {item['description']}")
                if item['price']:
                    print(f"    💰 {item['price']}")
    else:
        print("\n❌ No menu items found")
