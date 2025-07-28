# erste_campus_iframe_scraper.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import re
from typing import List, Dict, Optional
import locale

class ErsteCampusIframeScraper:
    """Scraper that directly targets the Erste Campus menu iframe."""
    
    def __init__(self):
        self.name = "Erste Campus"
        self.base_url = "https://erstecampus.at/en/kantine-am-campus-menu/"
        self.iframe_url = "https://erstecampus.at/mealplan/2025/external/single/kantine-en.html"
        
    def scrape(self) -> Optional[List[Dict]]:
        """Scrape the menu from the iframe URL."""
        print(f"\n🍽️ Scraping {self.name} from iframe")
        print("=" * 60)
        print(f"📍 Target URL: {self.iframe_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': self.base_url,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            response = requests.get(self.iframe_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Save the content for inspection
            with open('erste_campus_iframe_content.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Saved iframe content to 'erste_campus_iframe_content.html'")
            
            # Parse the content
            soup = BeautifulSoup(response.content, 'html.parser')
            menu_items = self._extract_menu_items(soup)
            
            if menu_items:
                print(f"\n✅ Successfully extracted {len(menu_items)} menu items!")
                return menu_items
            else:
                print("\n⚠️ No menu items found. Trying alternative parsing...")
                return self._alternative_parsing(soup)
                
        except requests.RequestException as e:
            print(f"\n❌ Request failed: {e}")
            return None
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    def _extract_menu_items(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract menu items from the parsed HTML."""
        menu_items = []
        
        # Strategy 1: Look for day containers
        print("\n🔍 Looking for menu structure...")
        
        # Common patterns for menu containers
        day_selectors = [
            {'class': re.compile(r'day|tag|daily|menu-day', re.I)},
            {'class': re.compile(r'meal|speise|menu-item', re.I)},
            {'id': re.compile(r'day|monday|tuesday|wednesday|thursday|friday', re.I)},
        ]
        
        # Try each selector
        for selector in day_selectors:
            containers = soup.find_all(['div', 'section', 'article', 'li'], **selector)
            if containers:
                print(f"  ✅ Found {len(containers)} containers with selector: {selector}")
                
                for container in containers:
                    items = self._parse_container(container)
                    menu_items.extend(items)
                    
                if menu_items:
                    break
                    
        # Strategy 2: Look for date patterns in text
        if not menu_items:
            print("\n🔍 Looking for date patterns in text...")
            menu_items = self._extract_by_date_patterns(soup)
            
        # Strategy 3: Table-based menu
        if not menu_items:
            print("\n🔍 Looking for table-based menu...")
            menu_items = self._extract_from_tables(soup)
            
        return menu_items
        
    def _parse_container(self, container) -> List[Dict]:
        """Parse a single day/menu container."""
        items = []
        
        # Extract date
        menu_date = self._extract_date_from_container(container)
        if not menu_date:
            menu_date = date.today()  # Fallback to today
            
        # Extract menu items
        # Look for text blocks that could be menu items
        text_elements = container.find_all(['p', 'li', 'div', 'span'])
        
        for elem in text_elements:
            text = elem.get_text(strip=True)
            
            # Filter out dates, headers, and short text
            if (len(text) > 15 and 
                not self._is_date_text(text) and 
                not self._is_header_text(text)):
                
                items.append({
                    'menu_date': menu_date,
                    'category': self._determine_category(text),
                    'description': self._clean_description(text),
                    'price': self._extract_price(text)
                })
                
        return items
        
    def _extract_date_from_container(self, container) -> Optional[date]:
        """Extract date from a container element."""
        # Look for date in various formats
        date_patterns = [
            (r'(\d{1,2})[.\s]+(\d{1,2})[.\s]+(\d{4})', '%d.%m.%Y'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
            (r'(\w+),?\s+(\d{1,2})[.\s]+(\w+)\s+(\d{4})', None),  # Monday, 25. July 2025
        ]
        
        text = container.get_text()
        
        for pattern, date_format in date_patterns:
            match = re.search(pattern, text)
            if match:
                if date_format:
                    try:
                        if len(match.groups()) == 3:
                            if '-' in pattern:
                                return datetime.strptime(f"{match.group(1)}-{match.group(2)}-{match.group(3)}", date_format).date()
                            else:
                                return datetime.strptime(f"{match.group(1)}.{match.group(2)}.{match.group(3)}", date_format).date()
                    except ValueError:
                        continue
                else:
                    # Handle named months
                    try:
                        day = int(match.group(2))
                        month_name = match.group(3)
                        year = int(match.group(4))
                        
                        # Convert month name to number
                        months = {
                            'january': 1, 'february': 2, 'march': 3, 'april': 4,
                            'may': 5, 'june': 6, 'july': 7, 'august': 8,
                            'september': 9, 'october': 10, 'november': 11, 'december': 12,
                            'januar': 1, 'februar': 2, 'märz': 3, 'april': 4,
                            'mai': 5, 'juni': 6, 'juli': 7, 'august': 8,
                            'september': 9, 'oktober': 10, 'november': 11, 'dezember': 12
                        }
                        
                        month = months.get(month_name.lower())
                        if month:
                            return date(year, month, day)
                    except (ValueError, KeyError):
                        continue
                        
        return None
        
    def _extract_by_date_patterns(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract menu items by finding dates first."""
        menu_items = []
        
        # Find all text containing dates
        date_pattern = re.compile(r'\d{1,2}[.\s/]+\d{1,2}[.\s/]+\d{4}')
        
        for element in soup.find_all(string=date_pattern):
            parent = element.parent
            
            # Find the date
            date_match = date_pattern.search(str(element))
            if date_match:
                try:
                    # Parse the date
                    date_text = date_match.group(0)
                    menu_date = self._parse_date_text(date_text)
                    
                    if menu_date:
                        # Look for menu items after this date
                        # Go up to find container
                        container = parent
                        while container and container.name not in ['div', 'section', 'article', 'td', 'li']:
                            container = container.parent
                            
                        if container:
                            # Find subsequent text that could be menu items
                            next_siblings = container.find_next_siblings()
                            texts = [container.get_text(strip=True)]
                            
                            for sibling in next_siblings[:5]:  # Check next 5 siblings
                                sibling_text = sibling.get_text(strip=True)
                                if self._is_date_text(sibling_text):
                                    break  # Stop at next date
                                texts.append(sibling_text)
                                
                            # Parse the collected texts
                            for text in texts:
                                if len(text) > 15 and not self._is_date_text(text) and not self._is_header_text(text):
                                    menu_items.append({
                                        'menu_date': menu_date,
                                        'category': self._determine_category(text),
                                        'description': self._clean_description(text),
                                        'price': self._extract_price(text)
                                    })
                                    
                except Exception as e:
                    print(f"  ⚠️ Error parsing date {date_text}: {e}")
                    continue
                    
        return menu_items
        
    def _extract_from_tables(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract menu from table structure."""
        menu_items = []
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            
            current_date = None
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                for cell in cells:
                    text = cell.get_text(strip=True)
                    
                    # Check if it's a date
                    if self._is_date_text(text):
                        current_date = self._parse_date_text(text)
                    elif current_date and len(text) > 15:
                        menu_items.append({
                            'menu_date': current_date,
                            'category': self._determine_category(text),
                            'description': self._clean_description(text),
                            'price': self._extract_price(text)
                        })
                        
        return menu_items
        
    def _alternative_parsing(self, soup: BeautifulSoup) -> List[Dict]:
        """Alternative parsing method when standard methods fail."""
        print("\n🔄 Trying alternative parsing methods...")
        
        # Get all text content and analyze structure
        all_text = soup.get_text()
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        
        menu_items = []
        current_date = None
        
        for i, line in enumerate(lines):
            # Check if line is a date
            if self._is_date_text(line):
                current_date = self._parse_date_text(line)
                print(f"  📅 Found date: {current_date}")
            
            # Check if line could be a menu item
            elif current_date and len(line) > 15 and not self._is_header_text(line):
                # Skip if it's too similar to previous line (duplicate)
                if i > 0 and lines[i-1] == line:
                    continue
                    
                menu_items.append({
                    'menu_date': current_date,
                    'category': self._determine_category(line),
                    'description': self._clean_description(line),
                    'price': self._extract_price(line)
                })
                
        return menu_items
        
    def _is_date_text(self, text: str) -> bool:
        """Check if text contains a date."""
        date_patterns = [
            r'\d{1,2}[.\s/]+\d{1,2}[.\s/]+\d{4}',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)',
        ]
        
        text_lower = text.lower()
        for pattern in date_patterns:
            if re.search(pattern, text_lower):
                return True
        return False
        
    def _is_header_text(self, text: str) -> bool:
        """Check if text is likely a header."""
        header_keywords = [
            'menu', 'speisekarte', 'woche', 'week', 'öffnungszeiten',
            'opening', 'hours', 'kantine', 'restaurant', 'erste campus'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in header_keywords) and len(text) < 50
        
    def _parse_date_text(self, text: str) -> Optional[date]:
        """Parse various date formats."""
        # Try standard formats
        formats = [
            '%d.%m.%Y',
            '%d. %m. %Y',
            '%d/%m/%Y',
            '%Y-%m-%d',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(text.strip(), fmt).date()
            except ValueError:
                continue
                
        # Try regex extraction
        match = re.search(r'(\d{1,2})[.\s/]+(\d{1,2})[.\s/]+(\d{4})', text)
        if match:
            try:
                day, month, year = match.groups()
                return date(int(year), int(month), int(day))
            except ValueError:
                pass
                
        return None
        
    def _determine_category(self, text: str) -> str:
        """Determine meal category from text."""
        text_lower = text.lower()
        
        categories = {
            'Soup': ['suppe', 'soup', 'brühe', 'broth'],
            'Salad': ['salat', 'salad'],
            'Vegetarian': ['vegetarisch', 'vegetarian', 'vegan', 'veggie'],
            'Fish': ['fisch', 'fish', 'lachs', 'salmon'],
            'Dessert': ['dessert', 'sweet', 'kuchen', 'cake', 'eis', 'ice cream'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
                
        return 'Main Dish'
        
    def _clean_description(self, text: str) -> str:
        """Clean menu item description."""
        # Remove prices
        text = re.sub(r'[€$]\s*\d+[,.]?\d*', '', text)
        text = re.sub(r'\d+[,.]?\d*\s*[€$]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common suffixes
        text = re.sub(r'\s*\(.*?\)\s*$', '', text)  # Remove parenthetical info at end
        
        return text.strip()
        
    def _extract_price(self, text: str) -> str:
        """Extract price from text."""
        # Look for Euro prices
        price_patterns = [
            r'[€]\s*(\d+[,.]?\d*)',
            r'(\d+[,.]?\d*)\s*[€]',
            r'EUR\s*(\d+[,.]?\d*)',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                price = match.group(1).replace(',', '.')
                return f"€ {price}"
                
        return ""


if __name__ == "__main__":
    scraper = ErsteCampusIframeScraper()
    results = scraper.scrape()
    
    if results:
        print(f"\n\n📊 Summary: Found {len(results)} menu items")
        
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
        print("\n\n❌ Failed to extract menu items")
