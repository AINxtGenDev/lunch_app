# erste_campus_final_scraper_fixed.py
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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ErsteCampusFinalScraper:
    """
    Final optimized scraper for Erste Campus menu.
    Handles dynamic content loading and multi-day extraction.
    """
    
    def __init__(self):
        self.name = "Erste Campus"
        self.iframe_url = "https://erstecampus.at/mealplan/2025/external/single/kantine-en.html"
        self.allergen_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L', 'M', 'N', 'O', 'P', 'R']
        self.logger = logger
        
    def scrape(self) -> Optional[List[Dict]]:
        """
        Main scraping method with improved parsing and multi-day support.
        
        Returns:
            List of menu items with date, category, description, and price
        """
        print(f"\n🍽️ Scraping {self.name} (Final Version)")
        print("=" * 60)
        
        # Configure Chrome options for stability
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = None
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            print(f"🔗 Loading: {self.iframe_url}")
            driver.get(self.iframe_url)
            
            # Wait for initial content to load
            self._wait_for_content(driver)
            
            # Extract the weekly menu
            menu_by_day = self._extract_weekly_menu(driver)
            
            # Convert to list format
            menu_items = []
            for date_obj, items in menu_by_day.items():
                for item in items:
                    item['menu_date'] = date_obj
                    menu_items.append(item)
            
            # Log summary
            if menu_items:
                print(f"\n✅ Total items scraped: {len(menu_items)}")
                unique_dates = len(set(item['menu_date'] for item in menu_items))
                print(f"📅 Days covered: {unique_dates}")
            
            return menu_items if menu_items else None
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.logger.error(f"Scraping failed: {e}", exc_info=True)
            return None
        finally:
            if driver:
                driver.quit()
                
    def _wait_for_content(self, driver, timeout: int = 10):
        """Wait for dynamic content to load."""
        try:
            # Wait for any of these indicators that content is loaded
            WebDriverWait(driver, timeout).until(
                lambda d: (
                    d.find_elements(By.CSS_SELECTOR, "[class*='meal']") or
                    d.find_elements(By.CSS_SELECTOR, "[class*='menu']") or
                    len(d.find_element(By.TAG_NAME, "body").text.strip()) > 100
                )
            )
            # Additional wait for JavaScript rendering
            time.sleep(2)
        except Exception as e:
            self.logger.warning(f"Timeout waiting for content: {e}")
            # Continue anyway, content might be partially loaded
                
    def _extract_weekly_menu(self, driver) -> Dict[date, List[Dict]]:
        """
        Extract menu for the entire week with improved day navigation.
        
        Returns:
            Dictionary mapping dates to lists of menu items
        """
        weekly_menu = OrderedDict()
        
        print("\n📅 Extracting weekly menu...")
        
        # First, extract current view
        current_content = self._extract_current_day_menu(driver)
        if current_content:
            date_obj, items = current_content
            if items:
                weekly_menu[date_obj] = items
                print(f"  ✅ {date_obj.strftime('%A, %d.%m.%Y')}: {len(items)} items")
        
        # Find and click day navigation elements
        try:
            # Multiple strategies to find day elements
            selectors = [
                "[class*='day-tab']",
                "[class*='weekday']",
                "button[class*='day']",
                "a[href*='date=']",
                "div[class*='day'][class*='cursor-pointer']"
            ]
            
            day_elements = []
            for selector in selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                day_elements.extend(elements)
            
            # Filter unique elements with dates
            unique_date_elements = self._filter_date_elements(day_elements)
            
            print(f"  Found {len(unique_date_elements)} unique days to extract")
            
            # Process each day
            for date_str, elem in unique_date_elements.items():
                try:
                    # Parse the date
                    date_obj = self._parse_date_string(date_str)
                    if not date_obj or date_obj in weekly_menu:
                        continue
                    
                    # Click the element
                    self._safe_click(driver, elem)
                    
                    # Wait for content to update
                    time.sleep(2)
                    
                    # Extract menu for this day
                    day_content = self._extract_current_day_menu(driver, expected_date=date_obj)
                    if day_content:
                        _, items = day_content
                        if items:
                            weekly_menu[date_obj] = items
                            print(f"  ✅ {date_obj.strftime('%A, %d.%m.%Y')}: {len(items)} items")
                    
                except Exception as e:
                    self.logger.warning(f"Error processing day {date_str}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in weekly extraction: {e}")
        
        return weekly_menu
        
    def _filter_date_elements(self, elements: List) -> OrderedDict:
        """
        Filter elements to find unique ones with dates.
        
        Returns:
            OrderedDict mapping date strings to elements
        """
        unique_dates = OrderedDict()
        
        for elem in elements:
            try:
                text = elem.text.strip()
                if not text:
                    continue
                    
                # Look for date patterns
                date_match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{2})', text)
                if date_match:
                    date_str = date_match.group(1)
                    if date_str not in unique_dates:
                        unique_dates[date_str] = elem
                        
            except Exception:
                continue
                
        return unique_dates
        
    def _safe_click(self, driver, element):
        """Safely click an element using JavaScript."""
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", element)
        except Exception as e:
            self.logger.warning(f"Click failed, trying alternative method: {e}")
            element.click()
        
    def _parse_date_string(self, date_str: str) -> Optional[date]:
        """Parse date string in format DD.MM.YY."""
        try:
            day, month, year = date_str.split('.')
            return date(2000 + int(year), int(month), int(day))
        except Exception:
            return None
            
    def _extract_current_day_menu(self, driver, expected_date: Optional[date] = None) -> Optional[Tuple[date, List[Dict]]]:
        """
        Extract menu items from the current view with improved parsing.
        
        Args:
            driver: Selenium WebDriver instance
            expected_date: Expected date for validation
            
        Returns:
            Tuple of (date, list of menu items) or None
        """
        try:
            # Get all visible text
            body_text = driver.find_element(By.TAG_NAME, "body").text
            lines = [line.strip() for line in body_text.split('\n') if line.strip()]
            
            # Find the current date
            current_date = expected_date or self._find_date_in_content(lines)
            if not current_date:
                current_date = date.today()
                
            # Parse menu items with improved logic
            menu_items = self._parse_menu_items(lines)
            
            # Remove duplicates and filter
            unique_items = self._deduplicate_items(menu_items)
            
            return (current_date, unique_items) if unique_items else None
            
        except Exception as e:
            self.logger.error(f"Error extracting day menu: {e}")
            return None
            
    def _find_date_in_content(self, lines: List[str]) -> Optional[date]:
        """Find date in the content lines."""
        for line in lines[:20]:  # Check first 20 lines
            date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{2})', line)
            if date_match:
                day, month, year = date_match.groups()
                try:
                    return date(2000 + int(year), int(month), int(day))
                except ValueError:
                    continue
        return None
        
    def _parse_menu_items(self, lines: List[str]) -> List[Dict]:
        """
        Parse menu items from text lines with improved structure detection.
        
        Returns:
            List of parsed menu items
        """
        menu_items = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a category header
            if line in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                category = self._normalize_category(line)
                i += 1
                
                # Process items under this category
                while i < len(lines) and lines[i] not in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                    item_data = self._extract_menu_item(lines, i)
                    if item_data:
                        item_lines, price, next_index = item_data
                        
                        description = ' '.join(item_lines)
                        cleaned_desc = self._clean_description(description)
                        
                        if cleaned_desc and len(cleaned_desc) > 10:
                            menu_items.append({
                                'category': category,
                                'description': cleaned_desc,
                                'price': price
                            })
                        
                        i = next_index
                    else:
                        i += 1
            else:
                i += 1
                
        return menu_items
        
    def _extract_menu_item(self, lines: List[str], start_index: int) -> Optional[Tuple[List[str], str, int]]:
        """
        Extract a single menu item starting from the given index.
        
        Returns:
            Tuple of (item_lines, price, next_index) or None
        """
        item_lines = []
        price = ''
        i = start_index
        
        while i < len(lines):
            current_line = lines[i]
            
            # Check for price
            if re.match(r'^€\s*\d+', current_line):
                price = current_line
                return (item_lines, price, i + 1)
                
            # Check for allergen codes only
            if self._is_allergen_line(current_line):
                return (item_lines, price, i + 1) if item_lines else None
                
            # Check for new category
            if current_line in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                return (item_lines, price, i) if item_lines else None
                
            # Add to current item
            item_lines.append(current_line)
            i += 1
            
        return (item_lines, price, i) if item_lines else None
        
    def _normalize_category(self, category_text: str) -> str:
        """Normalize category names to standard format."""
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
        if len(chars) == 0 or len(chars) > 10:  # Too long to be just allergens
            return False
        return all(c in self.allergen_codes for c in chars)
        
    def _clean_description(self, text: str) -> str:
        """
        Clean menu item description with improved filtering.
        
        Returns:
            Cleaned description or empty string if invalid
        """
        # Filter out URLs and technical content
        if any(pattern in text.lower() for pattern in [
            'http', 'www', '.html', '.php', 'external', 'single',
            'kantine-en', '?date=', 'href='
        ]):
            return ""
            
        # Remove category labels
        text = re.sub(r'^(SOUP|MAIN DISH|DESSERTS?|SALAD)\s*', '', text, flags=re.I)
        
        # Remove standalone allergen codes at the end
        text = re.sub(r'\s+[A-Z](\s+[A-Z])*\s*$', '', text)
        
        # Remove single letters that might be allergen codes
        text = re.sub(r'\b[A-Z]\b', '', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s*([/,])\s*', r' \1 ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
        
    def _deduplicate_items(self, items: List[Dict]) -> List[Dict]:
        """Remove duplicate items while preserving order."""
        unique_items = []
        seen = set()
        
        for item in items:
            # Create a key for comparison
            key = (item['category'], item['description'].lower())
            
            if key not in seen:
                seen.add(key)
                unique_items.append(item)
                
        return unique_items


def format_menu_output(menu_items: List[Dict]) -> None:
    """
    Format and display the menu items in a user-friendly way.
    
    Args:
        menu_items: List of menu item dictionaries
    """
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
            
        # Display in logical order
        category_order = ['Soup', 'Salad', 'Main Dish', 'Dessert']
        
        for category in category_order:
            if category in by_category:
                print(f"\n🍽️ {category}:")
                for item in by_category[category]:
                    print(f"  • {item['description']}")
                    if item.get('price'):
                        print(f"    💰 {item['price']}")


if __name__ == "__main__":
    # Run the scraper
    scraper = ErsteCampusFinalScraper()
    results = scraper.scrape()
    
    # Display formatted output
    format_menu_output(results)
    
    # Optionally save to JSON for inspection
    if results:
        import json
        with open('erste_campus_menu.json', 'w', encoding='utf-8') as f:
            # Convert date objects to strings for JSON serialization
            json_results = []
            for item in results:
                json_item = item.copy()
                json_item['menu_date'] = item['menu_date'].isoformat()
                json_results.append(json_item)
                
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        print("\n💾 Menu saved to 'erste_campus_menu.json'")
