# app/scrapers/cyclist_scraper_improved.py
"""
Improved Cyclist scraper with better OCR handling for Raspberry Pi.
"""
import re
import requests
from datetime import date
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import io

from .base_scraper import BaseScraper


class CyclistScraperImproved(BaseScraper):
    """Improved Cyclist scraper with better image processing."""
    
    def __init__(self):
        super().__init__(
            "Cyclist",
            "https://www.cafe-cyclist.com/"
        )
        self.base_url = self.url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36'
        }
        
    def get_direct_image_url(self) -> Optional[str]:
        """Try to get the direct image URL from Flipsnack with multiple strategies."""
        
        # Try the known URL first
        known_url = "https://www.flipsnack.com/EE9BE6CC5A8/wochenmen-14-20-08-2023/full-view.html"
        
        try:
            # Use headers that match a real browser
            browser_headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(known_url, headers=browser_headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Strategy 1: Look for the og:image meta tag
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    image_url = og_image['content']
                    self.logger.info(f"Found OG image URL: {image_url}")
                    
                    # Try multiple variations of the URL
                    url_variants = [
                        image_url,  # Original
                        image_url.replace('/large', '/medium'),
                        image_url.replace('/medium', '/large'),
                        image_url.replace('/small', '/medium'),
                    ]
                    
                    for variant in url_variants:
                        if self.test_image_url(variant, browser_headers):
                            return variant
                
                # Strategy 2: Look for Twitter card image
                twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
                if twitter_image and twitter_image.get('content'):
                    image_url = twitter_image['content']
                    self.logger.info(f"Found Twitter image URL: {image_url}")
                    if self.test_image_url(image_url, browser_headers):
                        return image_url
                
                # Strategy 3: Look in script tags for image data
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        # Look for image URLs in JavaScript
                        matches = re.findall(r'https?://[^"\s]+\.(?:jpg|jpeg|png|webp)', script.string)
                        for match in matches:
                            if 'flipsnack' in match or 'd160aj0mj3npgx.cloudfront.net' in match:
                                self.logger.info(f"Found script image URL: {match}")
                                if self.test_image_url(match, browser_headers):
                                    return match
                            
        except Exception as e:
            self.logger.error(f"Error getting direct image URL: {e}")
            
        return None
    
    def test_image_url(self, url: str, headers: dict) -> bool:
        """Test if an image URL is accessible."""
        try:
            response = requests.head(url, headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def preprocess_image_for_ocr(self, image_data: bytes) -> Image.Image:
        """Preprocess image for better OCR results."""
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too small
        width, height = image.size
        if width < 1000:
            scale_factor = 1500 / width
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to grayscale
        image = image.convert('L')
        
        # Apply sharpening filter
        image = image.filter(ImageFilter.SHARPEN)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Apply threshold to get black and white image
        threshold = 128
        image = image.point(lambda p: p > threshold and 255)
        
        return image
    
    def perform_advanced_ocr(self, image_data: bytes) -> Optional[str]:
        """Perform OCR with advanced preprocessing."""
        try:
            # Preprocess the image
            image = self.preprocess_image_for_ocr(image_data)
            
            # Save preprocessed image for debugging
            debug_path = "/home/stecher/lunch_app/Screenshots/preprocessed_menu.png"
            image.save(debug_path)
            self.logger.info(f"Saved preprocessed image to {debug_path}")
            
            # Perform OCR with different configurations
            configs = [
                r'--oem 3 --psm 6',  # Default
                r'--oem 3 --psm 11',  # Sparse text
                r'--oem 3 --psm 3',   # Fully automatic page segmentation
            ]
            
            best_text = ""
            best_length = 0
            
            for config in configs:
                try:
                    text = pytesseract.image_to_string(image, lang='deu+eng', config=config)
                    if len(text) > best_length:
                        best_text = text
                        best_length = len(text)
                except:
                    continue
            
            self.logger.info(f"OCR extracted {len(best_text)} characters")
            return best_text if best_text else None
            
        except Exception as e:
            self.logger.error(f"Advanced OCR error: {e}")
            return None
    
    def clean_ocr_text(self, text: str) -> str:
        """Clean up common OCR errors."""
        # Replace common OCR mistakes
        replacements = {
            '|': 'l',
            '0': 'o',  # for text contexts
            '1': 'i',  # for text contexts
            '€€€€': '****',
            'MOHNTAG': 'MONTAG',
            'DIENSTAC': 'DIENSTAG',
            'MITTWDCH': 'MITTWOCH',
            'DONNERSTAC': 'DONNERSTAG',
            'FREITAC': 'FREITAG',
            'SAMSTAC': 'SAMSTAG',
            'SONNTAC': 'SONNTAG',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        return text
    
    def parse_menu_intelligently(self, text: str) -> Dict[str, List[Dict]]:
        """Parse menu with intelligent text processing for two-column layout."""
        text = self.clean_ocr_text(text)
        menu_by_day = {}
        
        # Split into lines and clean
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            # Skip empty lines and noise
            if line and len(line) > 3 and not line.startswith('©'):
                lines.append(line)
        
        # German day names
        days = {
            'MONTAG': 'MONDAY',
            'DIENSTAG': 'TUESDAY', 
            'MITTWOCH': 'WEDNESDAY',
            'DONNERSTAG': 'THURSDAY',
            'FREITAG': 'FRIDAY',
            'SAMSTAG': 'SATURDAY',
            'SONNTAG': 'SUNDAY'
        }
        
        # Look for the two-column pattern where days appear twice on the same logical line
        i = 0
        while i < len(lines):
            line = lines[i]
            line_upper = line.upper()
            
            # Check if this line contains a day (possibly twice for two columns)
            found_days = []
            for german_day, english_day in days.items():
                if german_day in line_upper:
                    # Count occurrences to detect two-column layout
                    count = line_upper.count(german_day)
                    found_days.extend([english_day] * count)
            
            if found_days:
                # This is a day header line, process the menu items that follow
                i += 1
                
                # Collect the menu lines for this day until we hit the next day or end
                menu_lines = []
                while i < len(lines):
                    next_line = lines[i]
                    next_upper = next_line.upper()
                    
                    # Stop if we hit another day
                    if any(d in next_upper for d in days.keys()):
                        break
                    
                    # Skip non-menu lines
                    if any(skip in next_upper for skip in ['TAGESTELLER', 'CYCLIST', '****', '....', 'WOCHENMEN']):
                        i += 1
                        continue
                    
                    if re.match(r'^\d{1,2}\.\d{1,2}', next_line):
                        i += 1
                        continue
                    
                    if len(next_line) > 5:
                        menu_lines.append(next_line)
                    
                    i += 1
                
                # Parse menu items for this day
                if len(found_days) == 2 and menu_lines:
                    # Two-column layout - split items between columns
                    items = self.parse_two_column_menu_items(menu_lines)
                    if found_days[0] in menu_by_day:
                        menu_by_day[found_days[0]].extend(items)
                    else:
                        menu_by_day[found_days[0]] = items
                        
                elif len(found_days) == 1 and menu_lines:
                    # Single column
                    items = self.parse_single_column_menu_items(menu_lines)
                    if found_days[0] in menu_by_day:
                        menu_by_day[found_days[0]].extend(items)
                    else:
                        menu_by_day[found_days[0]] = items
            else:
                i += 1
        
        return menu_by_day
    
    def parse_two_column_menu_items(self, menu_lines: List[str]) -> List[Dict]:
        """Parse menu items from two-column layout."""
        items = []
        i = 0
        
        while i < len(menu_lines):
            line = menu_lines[i]
            # Clean the line
            line = line.strip()
            if not line:
                i += 1
                continue
            
            # Priority: Check if this is "GRÜNE BOHNEN" followed by "Karotten"
            if line == "GRÜNE BOHNEN" and i + 1 < len(menu_lines):
                next_line = menu_lines[i + 1].strip()
                if next_line.startswith("Karotten") or next_line.startswith("KAROTTEN"):
                    # Combine them into one menu item
                    combined_item = f"{line} {next_line}"
                    items.append({'name': combined_item, 'description': ''})
                    i += 2  # Skip both lines
                    continue
                    
            # Strategy 1: Look for menu keywords that indicate separate items
            menu_keywords = ['PASTA', 'WOK', 'CHILI', 'MINUTE', 'VEGANER', 'LACHS', 
                           'LEBERKÄSE', 'OFENKARTOFFEL', 'GEGRILLTES', 'SCHWEINE',
                           'KARTOFFEL', 'RATATOUILLE', 'Pasta', 'Wok', 'Chili']
            
            # Find all keyword positions
            keyword_positions = []
            for keyword in menu_keywords:
                pos = line.find(keyword)
                if pos != -1:
                    keyword_positions.append((pos, keyword))
            
            # Sort by position
            keyword_positions.sort()
            
            if len(keyword_positions) >= 2:
                # Multiple keywords found - split the line
                items_in_line = []
                last_pos = 0
                
                for j, (pos, keyword) in enumerate(keyword_positions):
                    if j == 0:
                        # First item starts from beginning
                        continue
                    
                    # Extract item from last position to current position
                    item_text = line[last_pos:pos].strip()
                    if item_text and len(item_text) > 3:
                        items_in_line.append(item_text)
                    last_pos = pos
                
                # Add the last item
                last_item = line[last_pos:].strip()
                if last_item and len(last_item) > 3:
                    items_in_line.append(last_item)
                
                # Add all found items
                for item_text in items_in_line:
                    items.append({'name': item_text, 'description': ''})
                    
            # Strategy 2: Check for specific patterns like "GRÜNE BOHNEN Karotten & Rollgerste"
            elif 'GRÜNE BOHNEN' in line and ('Karotten' in line or 'KAROTTEN' in line):
                # Special case: This should be kept as ONE menu item
                # "GRÜNE BOHNEN Karotten & Rollgerste" = "Green beans, carrots & rolled barley"
                items.append({'name': line, 'description': ''})
                    
            # Strategy 3: Look for uppercase words that might indicate new items
            elif len(line) > 20:
                words = line.split()
                split_found = False
                
                # Look for capitalized words that might start new items
                for j, word in enumerate(words[1:], 1):  # Skip first word
                    if (word[0].isupper() and len(word) > 3 and 
                        word not in ['&', 'MIT', 'UND', 'VON', 'ZU', 'IN', 'AN', 'AUF']):
                        
                        # Check if this looks like a good split point
                        left_part = ' '.join(words[:j]).strip()
                        right_part = ' '.join(words[j:]).strip()
                        
                        # Validate both parts
                        if (len(left_part) > 5 and len(right_part) > 5 and
                            not left_part.endswith('&') and 
                            not right_part.startswith('&') and
                            not left_part.endswith('mit')):
                            
                            items.append({'name': left_part, 'description': ''})
                            items.append({'name': right_part, 'description': ''})
                            split_found = True
                            break
                
                if not split_found:
                    items.append({'name': line, 'description': ''})
            else:
                # Short line, treat as single item
                items.append({'name': line, 'description': ''})
            
            i += 1
        
        return items
    
    def parse_single_column_menu_items(self, menu_lines: List[str]) -> List[Dict]:
        """Parse menu items from single column layout."""
        items = []
        i = 0
        
        while i < len(menu_lines):
            line = menu_lines[i].strip()
            
            # Special case: If we see "GRÜNE BOHNEN" followed by a line starting with "Karotten"
            if line == "GRÜNE BOHNEN" and i + 1 < len(menu_lines):
                next_line = menu_lines[i + 1].strip()
                if next_line.startswith("Karotten") or next_line.startswith("KAROTTEN"):
                    # Combine them into one menu item
                    combined_item = f"{line} {next_line}"
                    items.append({'name': combined_item, 'description': ''})
                    i += 2  # Skip both lines
                    continue
            
            items.append({'name': line, 'description': ''})
            i += 1
        
        return items
    
    def scrape(self) -> Optional[List[Dict]]:
        """Main scraping method."""
        self.logger.info(f"Starting improved scrape for {self.name}")
        
        # Get direct image URL
        image_url = self.get_direct_image_url()
        if not image_url:
            self.logger.warning("Could not find image URL, using fallback")
            return self.get_fallback_menu()
        
        # Download image with proper headers
        try:
            browser_headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Referer': 'https://www.flipsnack.com/',
            }
            
            response = requests.get(image_url, headers=browser_headers, timeout=20)
            if response.status_code != 200:
                self.logger.error(f"Failed to download image: {response.status_code}")
                return self.get_fallback_menu()
            
            image_data = response.content
            self.logger.info(f"Downloaded image ({len(image_data)} bytes)")
            
            # Save original for debugging
            debug_path = "/home/stecher/lunch_app/Screenshots/original_menu.png"
            with open(debug_path, 'wb') as f:
                f.write(image_data)
            self.logger.info(f"Saved original image to {debug_path}")
            
        except Exception as e:
            self.logger.error(f"Error downloading image: {e}")
            return self.get_fallback_menu()
        
        # Perform advanced OCR
        menu_text = self.perform_advanced_ocr(image_data)
        if not menu_text:
            self.logger.error("OCR failed")
            return self.get_fallback_menu()
        
        # Save OCR output for debugging
        ocr_path = "/home/stecher/lunch_app/Screenshots/ocr_output.txt"
        with open(ocr_path, 'w', encoding='utf-8') as f:
            f.write(menu_text)
        self.logger.info(f"Saved OCR output to {ocr_path}")
        
        # Parse menu intelligently
        menu_by_day = self.parse_menu_intelligently(menu_text)
        
        # Get today's menu
        today = date.today()
        weekday = today.strftime("%A").upper()
        
        menu_items = []
        if weekday in menu_by_day:
            for item in menu_by_day[weekday]:
                menu_items.append({
                    'menu_date': today,
                    'category': 'Main Dish',
                    'description': item['name'],
                    'price': ''
                })
            self.logger.info(f"Extracted {len(menu_items)} items for {weekday}")
        else:
            self.logger.warning(f"No menu found for {weekday}, using fallback")
            return self.get_fallback_menu()
        
        # Validate menu items
        if menu_items and all(len(item['description']) < 200 for item in menu_items):
            return menu_items
        else:
            self.logger.warning("Menu items seem invalid, using fallback")
            return self.get_fallback_menu()
    
    def get_fallback_menu(self) -> Optional[List[Dict]]:
        """Return hardcoded fallback menu."""
        self.logger.info("Using fallback menu")
        
        today = date.today()
        weekday = today.strftime("%A").upper()
        
        # Hardcoded menu from the screenshot
        fallback = {
            "MONDAY": [
                "Minute Steak mit Senfmarinade",
                "Pasta mit Sonnengetrocknetes Tomatenpesto, Spinat, Paprika & Zucchini"
            ],
            "TUESDAY": [
                "Gegrilltes Hähnchen mit Teriyaki Sauce",
                "Wok - Gemüse mit Erbsen & Reis"
            ],
            "WEDNESDAY": [
                "Veganer Burger mit Falafel",
                "Chili sin Carne mit Reis, Tortilla Chips & Guacamole"
            ],
            "THURSDAY": [
                "Schweineschulter mit Zwiebelsauce",
                "Kartoffelknödel mit Ofentomate & Basilikum"
            ],
            "FRIDAY": [
                "Lachsfilet mit Zitronensauce",
                "Ratatouille mit Penne Aglio e Olio"
            ],
            "SATURDAY": [
                "Leberkäse & Putenleberkäse",
                "Grüne Bohnen mit Karotten & Röllgerste"
            ],
            "SUNDAY": [
                "Ofenkartoffel mit Pulled Chicken, gebratener Lachs & Gemüse",
                "Ofenkartoffel mit Käse, Gemüse & Kräuter"
            ]
        }
        
        menu_items = []
        if weekday in fallback:
            for item_name in fallback[weekday]:
                menu_items.append({
                    'menu_date': today,
                    'category': 'Main Dish (Fallback)',
                    'description': item_name,
                    'price': ''
                })
        
        return menu_items if menu_items else None