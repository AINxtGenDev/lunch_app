# erste_campus_selenium_scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from datetime import datetime, date
from typing import List, Dict, Optional

class ErsteCampusSeleniumScraper:
    """Use Selenium to wait for JavaScript to load the menu."""
    
    def __init__(self):
        self.name = "Erste Campus"
        self.iframe_url = "https://erstecampus.at/mealplan/2025/external/single/kantine-en.html"
        
    def scrape(self) -> Optional[List[Dict]]:
        """Scrape using Selenium to handle dynamic content."""
        print(f"\n🌐 Scraping {self.name} with Selenium")
        print("=" * 60)
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = None
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            print(f"🔗 Loading: {self.iframe_url}")
            driver.get(self.iframe_url)
            
            # Wait for content to load
            print("⏳ Waiting for dynamic content to load...")
            time.sleep(5)  # Initial wait
            
            # Try multiple strategies to find menu content
            menu_items = []
            
            # Strategy 1: Wait for specific elements
            print("\n🔍 Strategy 1: Looking for meal containers...")
            try:
                meal_containers = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='meal'], [class*='menu'], [class*='dish']"))
                )
                print(f"  Found {len(meal_containers)} potential meal containers")
                
                for container in meal_containers:
                    text = container.text.strip()
                    if len(text) > 20:
                        menu_items.append({
                            'menu_date': date.today(),
                            'category': 'Main Dish',
                            'description': text,
                            'price': ''
                        })
            except:
                print("  No meal containers found")
                
            # Strategy 2: Check for React/Next.js rendered content
            print("\n🔍 Strategy 2: Checking for React components...")
            try:
                # Execute JavaScript to get React props
                react_data = driver.execute_script("""
                    // Try to find React fiber
                    const findReactFiber = (element) => {
                        for (const key in element) {
                            if (key.startsWith('__reactFiber') || key.startsWith('__reactInternalInstance')) {
                                return element[key];
                            }
                        }
                        return null;
                    };
                    
                    // Try to get menu data from various sources
                    let menuData = null;
                    
                    // Check window object
                    if (window.__NEXT_DATA__) {
                        menuData = window.__NEXT_DATA__;
                    } else if (window.menuData) {
                        menuData = window.menuData;
                    } else if (window.__INITIAL_STATE__) {
                        menuData = window.__INITIAL_STATE__;
                    }
                    
                    // Try to find menu in DOM elements
                    if (!menuData) {
                        const elements = document.querySelectorAll('[data-menu], [data-meals], [class*="meal"]');
                        if (elements.length > 0) {
                            menuData = Array.from(elements).map(el => ({
                                text: el.textContent,
                                html: el.innerHTML
                            }));
                        }
                    }
                    
                    return menuData;
                """)
                
                if react_data:
                    print(f"  ✅ Found React data: {type(react_data)}")
                    with open('react_data.json', 'w', encoding='utf-8') as f:
                        json.dump(react_data, f, indent=2, ensure_ascii=False)
                    print("  💾 Saved to react_data.json")
            except Exception as e:
                print(f"  ❌ No React data found: {e}")
                
            # Strategy 3: Get all text content after full load
            print("\n🔍 Strategy 3: Extracting all visible text...")
            
            # Wait a bit more for lazy loading
            time.sleep(3)
            
            # Get the page source after JavaScript execution
            page_source = driver.page_source
            with open('selenium_rendered.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print("  💾 Saved rendered HTML to 'selenium_rendered.html'")
            
            # Get all visible text
            body_text = driver.find_element(By.TAG_NAME, "body").text
            lines = [line.strip() for line in body_text.split('\n') if line.strip()]
            
            print(f"  Found {len(lines)} lines of text")
            print("\n  First 10 lines:")
            for i, line in enumerate(lines[:10]):
                print(f"    {i+1}. {line}")
                
            # Parse the text for menu items
            current_date = date.today()
            for line in lines:
                # Skip headers, times, and short text
                if (len(line) > 30 and 
                    'Uhr' not in line and 
                    not line.startswith('11:00') and
                    'ENDE' not in line):
                    
                    # Check if it contains food-related keywords
                    food_keywords = ['suppe', 'salat', 'dessert', 'obst', 'buffet', 
                                   'soup', 'salad', 'dessert', 'fruit', 'menu']
                    
                    if any(keyword in line.lower() for keyword in food_keywords):
                        menu_items.append({
                            'menu_date': current_date,
                            'category': self._determine_category(line),
                            'description': self._clean_description(line),
                            'price': self._extract_price(line)
                        })
                        
            # Strategy 4: Click on day tabs if present
            print("\n🔍 Strategy 4: Looking for day navigation...")
            try:
                day_tabs = driver.find_elements(By.CSS_SELECTOR, "[class*='day-tab'], [class*='weekday'], button")
                if day_tabs:
                    print(f"  Found {len(day_tabs)} day tabs")
                    
                    for tab in day_tabs[:5]:  # Check first 5 tabs
                        try:
                            tab_text = tab.text.strip()
                            if tab_text:
                                print(f"    Clicking on: {tab_text}")
                                driver.execute_script("arguments[0].click();", tab)
                                time.sleep(2)
                                
                                # Extract content after clicking
                                content = driver.find_element(By.TAG_NAME, "body").text
                                new_lines = [line.strip() for line in content.split('\n') 
                                           if line.strip() and len(line.strip()) > 30]
                                
                                for line in new_lines:
                                    if not any(existing['description'] in line for existing in menu_items):
                                        menu_items.append({
                                            'menu_date': self._parse_weekday_to_date(tab_text),
                                            'category': self._determine_category(line),
                                            'description': self._clean_description(line),
                                            'price': self._extract_price(line)
                                        })
                        except:
                            continue
            except:
                print("  No day tabs found")
                
            return menu_items if menu_items else None
            
        except Exception as e:
            print(f"❌ Selenium error: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            if driver:
                driver.quit()
                
    def _determine_category(self, text: str) -> str:
        """Determine meal category."""
        text_lower = text.lower()
        
        if 'suppe' in text_lower or 'soup' in text_lower:
            return 'Soup'
        elif 'salat' in text_lower or 'salad' in text_lower:
            return 'Salad'
        elif 'dessert' in text_lower or 'obst' in text_lower:
            return 'Dessert'
        else:
            return 'Main Dish'
            
    def _clean_description(self, text: str) -> str:
        """Clean the description."""
        # Remove "Menü:" prefix
        text = text.replace('Menü:', '').replace('Menu:', '')
        
        # Fix encoding
        text = text.replace('Ã¼', 'ü').replace('Ã¶', 'ö').replace('Ã¤', 'ä')
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text.strip()
        
    def _extract_price(self, text: str) -> str:
        """Extract price if present."""
        import re
        price_match = re.search(r'€\s*(\d+[,.]?\d*)', text)
        if price_match:
            return f"€ {price_match.group(1)}"
        return ""
        
    def _parse_weekday_to_date(self, weekday_text: str) -> date:
        """Convert weekday text to date."""
        from datetime import timedelta
        
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 
            'friday': 4, 'saturday': 5, 'sunday': 6,
            'montag': 0, 'dienstag': 1, 'mittwoch': 2, 'donnerstag': 3,
            'freitag': 4, 'samstag': 5, 'sonntag': 6
        }
        
        today = date.today()
        current_weekday = today.weekday()
        
        for day_name, day_num in weekdays.items():
            if day_name in weekday_text.lower():
                days_diff = day_num - current_weekday
                return today + timedelta(days=days_diff)
                
        return today


if __name__ == "__main__":
    scraper = ErsteCampusSeleniumScraper()
    results = scraper.scrape()
    
    if results:
        print(f"\n\n✅ Found {len(results)} menu items!")
        for i, item in enumerate(results, 1):
            print(f"\n{i}. {item['menu_date'].strftime('%A, %d.%m.%Y')}")
            print(f"   Category: {item['category']}")
            print(f"   Description: {item['description']}")
            if item['price']:
                print(f"   Price: {item['price']}")
    else:
        print("\n❌ No menu items found")
