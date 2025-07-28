# erste_campus_advanced_scraper.py
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from datetime import datetime, date
import json

class ErsteCampusAdvancedScraper:
    """Advanced scraper that tries multiple strategies."""
    
    def __init__(self):
        self.name = "Erste Campus"
        self.url = "https://erstecampus.at/en/kantine-am-campus-menu/"
        
    def scrape(self):
        """Try multiple scraping strategies."""
        print(f"\n🍽️ Scraping {self.name}")
        print("=" * 60)
        
        # Strategy 1: Try direct web scraping
        results = self._scrape_static_content()
        if results:
            return results
            
        # Strategy 2: Try Selenium with iframe handling
        results = self._scrape_with_selenium()
        if results:
            return results
            
        # Strategy 3: Try to find and scrape Gourmet widget directly
        results = self._scrape_gourmet_widget()
        if results:
            return results
            
        print("\n❌ All scraping strategies failed!")
        return None
        
    def _scrape_static_content(self):
        """Try to scrape static content."""
        print("\n📋 Strategy 1: Static content scraping...")
        
        try:
            response = requests.get(self.url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            menu_items = []
            
            # Look for menu patterns in the HTML
            # Pattern 1: Look for date headers followed by menu items
            date_pattern = re.compile(r'(\d{1,2})[.\s]+(\d{1,2})[.\s]+(\d{4})')
            
            for element in soup.find_all(text=date_pattern):
                date_match = date_pattern.search(str(element))
                if date_match:
                    try:
                        menu_date = datetime.strptime(
                            f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}", 
                            "%d.%m.%Y"
                        ).date()
                        
                        # Find menu items near this date
                        parent = element.parent
                        while parent and parent.name not in ['div', 'section', 'article']:
                            parent = parent.parent
                            
                        if parent:
                            items = parent.find_all(['p', 'li', 'div'], 
                                                  string=re.compile(r'.{10,}'))  # At least 10 chars
                            for item in items[:5]:  # Max 5 items per day
                                text = item.get_text(strip=True)
                                if text and not date_pattern.match(text):
                                    menu_items.append({
                                        'menu_date': menu_date,
                                        'category': 'Main Dish',
                                        'description': text,
                                        'price': self._extract_price(text)
                                    })
                    except ValueError:
                        continue
                        
            if menu_items:
                print(f"  ✅ Found {len(menu_items)} items via static scraping")
                return menu_items
                
        except Exception as e:
            print(f"  ❌ Static scraping failed: {e}")
            
        return None
        
    def _scrape_with_selenium(self):
        """Use Selenium to handle JavaScript and iframes."""
        print("\n🌐 Strategy 2: Selenium with iframe handling...")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        driver = None
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            driver.get(self.url)
            time.sleep(5)  # Wait for JavaScript to load
            
            menu_items = []
            
            # Check for iframes
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute('src') or ''
                
                if any(keyword in src.lower() for keyword in ['gourmet', 'menu', 'speise']):
                    print(f"  🎯 Found relevant iframe: {src}")
                    
                    # Switch to iframe
                    driver.switch_to.frame(iframe)
                    time.sleep(3)
                    
                    # Try to extract menu from iframe
                    iframe_items = self._extract_menu_from_page(driver.page_source)
                    menu_items.extend(iframe_items)
                    
                    # Switch back
                    driver.switch_to.default_content()
                    
            # Also check main page content
            main_items = self._extract_menu_from_page(driver.page_source)
            menu_items.extend(main_items)
            
            if menu_items:
                print(f"  ✅ Found {len(menu_items)} items via Selenium")
                return menu_items
                
        except Exception as e:
            print(f"  ❌ Selenium scraping failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if driver:
                driver.quit()
                
        return None
        
    def _scrape_gourmet_widget(self):
        """Try to access Gourmet widget directly."""
        print("\n🍴 Strategy 3: Direct Gourmet widget access...")
        
        # Possible Gourmet customer IDs for Erste Campus
        customer_ids = [
            'erste-campus',
            'erste-bank',
            'erste-campus-vienna',
            'EAT-01011001',
            '01011001'
        ]
        
        base_urls = [
            'https://www.gourmet.at/widget/menu/',
            'https://widget.gourmet.at/menu/',
            'https://www.gourmet-group.at/widget/'
        ]
        
        for base_url in base_urls:
            for customer_id in customer_ids:
                url = f"{base_url}{customer_id}"
                print(f"  🔍 Trying: {url}")
                
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        items = self._extract_menu_from_page(response.text)
                        if items:
                            print(f"  ✅ Success with {url}")
                            return items
                except:
                    continue
                    
        return None
        
    def _extract_menu_from_page(self, html_content):
        """Extract menu items from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        menu_items = []
        
        # Multiple extraction patterns
        patterns = [
            # Pattern 1: Day containers with class names
            {
                'container': {'class': re.compile('day|tag|menu-day', re.I)},
                'date': {'class': re.compile('date|datum', re.I)},
                'items': {'class': re.compile('meal|dish|speise|menu-item', re.I)}
            },
            # Pattern 2: Table-based menus
            {
                'container': 'tr',
                'date': 'td',
                'items': 'td'
            }
        ]
        
        # Try each pattern
        for pattern in patterns:
            containers = soup.find_all(pattern['container'])
            
            for container in containers:
                # Extract date
                date_elem = container.find(pattern['date']) if isinstance(pattern['date'], dict) else container.find(pattern['date'])
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    menu_date = self._parse_date(date_text)
                    
                    if menu_date:
                        # Extract items
                        items = container.find_all(pattern['items']) if isinstance(pattern['items'], dict) else container.find_all(pattern['items'])
                        
                        for item in items:
                            text = item.get_text(strip=True)
                            if len(text) > 10 and not self._is_date(text):
                                menu_items.append({
                                    'menu_date': menu_date,
                                    'category': self._determine_category(text),
                                    'description': self._clean_description(text),
                                    'price': self._extract_price(text)
                                })
                                
        return menu_items
        
    def _parse_date(self, date_text):
        """Parse various date formats."""
        date_formats = [
            "%d.%m.%Y",
            "%d. %m. %Y",
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d %B %Y",
            "%B %d, %Y"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_text.strip(), fmt).date()
            except ValueError:
                continue
                
        # Try regex for partial matches
        match = re.search(r'(\d{1,2})[.\s/]+(\d{1,2})[.\s/]+(\d{4})', date_text)
        if match:
            try:
                return datetime.strptime(
                    f"{match.group(1)}.{match.group(2)}.{match.group(3)}", 
                    "%d.%m.%Y"
                ).date()
            except:
                pass
                
        return None
        
    def _is_date(self, text):
        """Check if text is likely a date."""
        return bool(re.search(r'\d{1,2}[.\s/]+\d{1,2}[.\s/]+\d{4}', text))
        
    def _determine_category(self, text):
        """Determine meal category from text."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['suppe', 'soup']):
            return 'Soup'
        elif any(word in text_lower for word in ['salat', 'salad']):
            return 'Salad'
        elif any(word in text_lower for word in ['dessert', 'sweet', 'kuchen']):
            return 'Dessert'
        elif any(word in text_lower for word in ['vegetarisch', 'vegetarian', 'vegan']):
            return 'Vegetarian'
        else:
            return 'Main Dish'
            
    def _clean_description(self, text):
        """Clean menu item description."""
        # Remove price if present
        text = re.sub(r'€\s*\d+[,.]?\d*', '', text)
        text = re.sub(r'\d+[,.]?\d*\s*€', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
        
    def _extract_price(self, text):
        """Extract price from text."""
        price_match = re.search(r'€\s*(\d+[,.]?\d*)', text)
        if not price_match:
            price_match = re.search(r'(\d+[,.]?\d*)\s*€', text)
            
        if price_match:
            return f"€ {price_match.group(1)}"
            
        return ""


if __name__ == "__main__":
    scraper = ErsteCampusAdvancedScraper()
    results = scraper.scrape()
    
    if results:
        print(f"\n\n✅ Final Results: {len(results)} menu items found!")
        print("\n📋 Sample items:")
        for item in results[:3]:
            print(f"\n📅 {item['menu_date']}")
            print(f"🏷️  {item['category']}")
            print(f"📝 {item['description']}")
            print(f"💰 {item['price'] or 'N/A'}")
    else:
        print("\n\n❌ No menu items could be extracted.")
