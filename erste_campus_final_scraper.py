# erste_campus_final_scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from collections import OrderedDict

class ErsteCampusFinalScraper:
    """Final optimized scraper for Erste Campus menu."""
    
    def __init__(self):
        self.name = "Erste Campus"
        self.iframe_url = "https://erstecampus.at/mealplan/2025/external/single/kantine-en.html"
        self.allergen_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L', 'M', 'N', 'O', 'P', 'R']
        
    def scrape(self) -> Optional[List[Dict]]:
        """Main scraping method with improved parsing."""
        print(f"\n🍽️ Scraping {self.name} (Final Version)")
        print("=" * 60)
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        driver = None
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            print(f"🔗 Loading: {self.iframe_url}")
            driver.get(self.iframe_url)
            
            # Wait for content to load
            time.sleep(5)
            
            # Extract the weekly menu
            menu_by_day = self._extract_weekly_menu(driver)
            
            # Convert to list format
            menu_items = []
            for date_obj, items in menu_by_day.items():
                for item in items:
                    item['menu_date'] = date_obj
                    menu_items.append(item)
            
            return menu_items if menu_items else None
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            if driver:
                driver.quit()
                
    def _extract_weekly_menu(self, driver) -> Dict[date, List[Dict]]:
        """Extract menu for the entire week."""
        weekly_menu = OrderedDict()
        
        # Get the day navigation elements
        print("\n📅 Extracting weekly menu...")
        
        # First, get the current view (usually Monday)
        current_content = self._extract_current_day_menu(driver)
        if current_content:
            date_obj, items = current_content
            if items:
                weekly_menu[date_obj] = items
                print(f"  ✅ {date_obj.strftime('%A, %d.%m.%Y')}: {len(items)} items")
        
        # Try to click through other days
        try:
            # Find day buttons/tabs
            day_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='day-tab'], [class*='weekday'], button")
            
            # Extract day information
            day_buttons = []
            for elem in day_elements:
                text = elem.text.strip()
                # Look for patterns like "TUE\n29.07.25" or just dates
                if re.search(r'\d{1,2}\.\d{1,2}\.\d{2}', text) or text in ['MON', 'TUE', 'WED', 'THU', 'FRI']:
                    day_buttons.append(elem)
            
            print(f"\n  Found {len(day_buttons)} day navigation elements")
            
            # Click each day and extract menu
            for i, day_elem in enumerate(day_buttons[:5]):  # Limit to 5 days (work week)
                try:
                    day_text = day_elem.text.strip()
                    
                    # Skip if already processed
                    date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{2})', day_text)
                    if date_match:
                        day, month, year = date_match.groups()
                        date_obj = date(2000 + int(year), int(month), int(day))
                        
                        if date_obj in weekly_menu:
                            continue
                    
                    # Click the day
                    driver.execute_script("arguments[0].click();", day_elem)
                    time.sleep(2)  # Wait for content to load
                    
                    # Extract menu for this day
                    day_content = self._extract_current_day_menu(driver)
                    if day_content:
                        date_obj, items = day_content
                        if items and date_obj not in weekly_menu:
                            weekly_menu[date_obj] = items
                            print(f"  ✅ {date_obj.strftime('%A, %d.%m.%Y')}: {len(items)} items")
                            
                except Exception as e:
                    print(f"  ⚠️ Error clicking day {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"  ⚠️ Error navigating days: {e}")
            
        return weekly_menu
        
    def _extract_current_day_menu(self, driver) -> Optional[Tuple[date, List[Dict]]]:
        """Extract menu items from the current view."""
        try:
            # Get all visible text
            body_text = driver.find_element(By.TAG_NAME, "body").text
            lines = [line.strip() for line in body_text.split('\n') if line.strip()]
            
            # Find the current date
            current_date = None
            for line in lines[:20]:  # Check first 20 lines for date
                date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{2})', line)
                if date_match:
                    day, month, year = date_match.groups()
                    current_date = date(2000 + int(year), int(month), int(day))
                    break
                    
            if not current_date:
                current_date = date.today()
                
            # Parse menu items
            menu_items = []
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # Check if this is a category header
                if line in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                    category = self._normalize_category(line)
                    
                    # Collect items under this category
                    i += 1
                    while i < len(lines) and lines[i] not in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                        item_lines = []
                        
                        # Collect lines until we hit a price or next item
                        while i < len(lines):
                            current_line = lines[i]
                            
                            # Check if this is a price line
                            if re.match(r'^€\s*\d+', current_line):
                                price = current_line
                                i += 1
                                break
                            # Check if this is allergen codes only
                            elif self._is_allergen_line(current_line):
                                i += 1
                                break
                            # Check if this is the start of a new item (another category)
                            elif current_line in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                                break
                            else:
                                item_lines.append(current_line)
                                i += 1
                                
                        # Create menu item if we have content
                        if item_lines:
                            description = ' '.join(item_lines)
                            if len(description) > 10:  # Filter out very short items
                                menu_items.append({
                                    'category': category,
                                    'description': self._clean_description(description),
                                    'price': price if 'price' in locals() else ''
                                })
                        
                        # Clear price for next item
                        if 'price' in locals():
                            del price
                else:
                    i += 1
                    
            # Remove duplicates while preserving order
            unique_items = []
            seen = set()
            for item in menu_items:
                item_key = (item['category'], item['description'])
                if item_key not in seen:
                    seen.add(item_key)
                    unique_items.append(item)
                    
            return (current_date, unique_items) if unique_items else None
            
        except Exception as e:
            print(f"  ❌ Error extracting day menu: {e}")
            return None
            
    def _normalize_category(self, category_text: str) -> str:
        """Normalize category names."""
        category_map = {
            'SOUP': 'Soup',
            'MAIN DISH': 'Main Dish',
            'DESSERTS': 'Dessert',
            'DESSERT': 'Dessert',
            'SALAD': 'Salad',
        }
        return category_map.get(category_text.upper(), 'Main Dish')
        
    def _is_allergen_line(self, line: str) -> bool:
        """Check if a line contains only allergen codes."""
        # Remove spaces and check if all characters are allergen codes
        chars = line.replace(' ', '')
        if len(chars) == 0:
            return False
        return all(c in self.allergen_codes for c in chars)
        
    def _clean_description(self, text: str) -> str:
        """Clean menu item description."""
        # Remove category labels
        text = re.sub(r'^(SOUP|MAIN DISH|DESSERTS?|SALAD)\s*', '', text, flags=re.I)
        
        # Remove standalone allergen codes at the end
        text = re.sub(r'\s+[A-Z](\s+[A-Z])*\s*$', '', text)
        
        # Fix common formatting issues
        text = text.replace('/', ' / ')  # Add spaces around slashes
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
        
    def _parse_date_from_navigation(self, nav_text: str) -> Optional[date]:
        """Parse date from navigation element text."""
        # Look for date pattern
        date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{2})', nav_text)
        if date_match:
            day, month, year = date_match.groups()
            return date(2000 + int(year), int(month), int(day))
            
        # Look for weekday and calculate date
        weekdays = {
            'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4,
            'MONDAY': 0, 'TUESDAY': 1, 'WEDNESDAY': 2, 'THURSDAY': 3, 'FRIDAY': 4
        }
        
        for day_name, day_num in weekdays.items():
            if day_name in nav_text.upper():
                # Get current week's date for this weekday
                today = date.today()
                days_ahead = day_num - today.weekday()
                if days_ahead < 0:  # Already passed this week
                    days_ahead += 7
                return today + timedelta(days_ahead)
                
        return None


def format_menu_output(menu_items: List[Dict]) -> None:
    """Format and display the menu items nicely."""
    if not menu_items:
        print("\n❌ No menu items found")
        return
        
    # Group by date
    from collections import defaultdict
    by_date = defaultdict(list)
    for item in menu_items:
        by_date[item['menu_date']].append(item)
        
    print(f"\n✅ Found menu for {len(by_date)} days")
    print("=" * 60)
    
    for menu_date in sorted(by_date.keys()):
        items = by_date[menu_date]
        print(f"\n📅 {menu_date.strftime('%A, %d %B %Y')}")
        print("-" * 40)
        
        # Group by category
        by_category = defaultdict(list)
        for item in items:
            by_category[item['category']].append(item)
            
        # Display in order: Soup, Main Dish, Salad, Dessert
        category_order = ['Soup', 'Main Dish', 'Salad', 'Dessert']
        
        for category in category_order:
            if category in by_category:
                print(f"\n🍽️ {category}:")
                for item in by_category[category]:
                    print(f"  • {item['description']}")
                    if item['price']:
                        print(f"    💰 {item['price']}")


if __name__ == "__main__":
    scraper = ErsteCampusFinalScraper()
    results = scraper.scrape()
    format_menu_output(results)
