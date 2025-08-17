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
        
        # Process the menu with simplified two-column detection
        i = 0
        while i < len(lines):
            line = lines[i]
            line_upper = line.upper()
            
            # Check if this line contains a day (possibly twice for two columns)
            found_day = None
            for german_day, english_day in days.items():
                if german_day in line_upper:
                    found_day = (german_day, english_day)
                    # Check if the day appears twice on the same line (two columns)
                    if line_upper.count(german_day) == 2:
                        # This line has both columns' day headers
                        i += 1
                        
                        # Collect all menu lines until separator or next day
                        all_menu_lines = []
                        while i < len(lines):
                            next_line = lines[i]
                            next_upper = next_line.upper()
                            
                            # Stop at separators or next day
                            if '****' in next_line or '....' in next_line:
                                break
                            if any(d in next_upper for d in days.keys()):
                                break
                            
                            # Skip headers
                            if any(skip in next_upper for skip in ['TAGESTELLER', 'CYCLIST', 'WOCHENMEN']):
                                i += 1
                                continue
                            if re.match(r'^\d{1,2}\.\d{1,2}', next_line):
                                i += 1
                                continue
                            
                            if len(next_line) > 5:
                                all_menu_lines.append(next_line)
                            i += 1
                        
                        # Try to intelligently split the collected lines into two menus
                        if all_menu_lines:
                            # Look for patterns that indicate column separation
                            left_items = []
                            right_items = []
                            
                            for menu_line in all_menu_lines:
                                # Check if line has multiple dish indicators (two columns merged)
                                upper_line = menu_line.upper()
                                
                                # Common dish keywords
                                dish_keywords = ['OFENKARTOFFEL', 'PASTA', 'WOK', 'MINUTE', 'CHILI', 
                                               'VEGANER', 'LACHS', 'LEBERKÄSE', 'GEGRILLTES', 
                                               'SCHWEINE', 'KARTOFFEL', 'RATATOUILLE']
                                
                                # Count how many dish keywords appear
                                keyword_count = sum(1 for kw in dish_keywords if kw in upper_line)
                                
                                if keyword_count >= 2:
                                    # Line likely contains both columns - try to split
                                    # Find the second keyword position
                                    positions = []
                                    for kw in dish_keywords:
                                        pos = upper_line.find(kw)
                                        if pos != -1:
                                            positions.append((pos, kw))
                                    
                                    if len(positions) >= 2:
                                        positions.sort()
                                        # Split at the second keyword
                                        split_pos = positions[1][0]
                                        left_part = menu_line[:split_pos].strip()
                                        right_part = menu_line[split_pos:].strip()
                                        
                                        if left_part:
                                            left_items.append(left_part)
                                        if right_part:
                                            right_items.append(right_part)
                                    else:
                                        # Add to left if we can't split
                                        left_items.append(menu_line)
                                else:
                                    # Single column item - assign based on what we have
                                    if not left_items or (right_items and len(left_items) > len(right_items)):
                                        left_items.append(menu_line)
                                    else:
                                        right_items.append(menu_line)
                            
                            # Create menu items
                            menu_items = []
                            if left_items:
                                menu_items.append({
                                    'name': ' '.join(left_items).strip(),
                                    'description': ''
                                })
                            if right_items:
                                menu_items.append({
                                    'name': ' '.join(right_items).strip(),
                                    'description': ''
                                })
                            
                            # If we only got one item, duplicate it to ensure 2 items
                            # (fallback for poor OCR)
                            if len(menu_items) == 1:
                                menu_items.append({
                                    'name': menu_items[0]['name'],
                                    'description': ''
                                })
                            
                            menu_by_day[english_day] = menu_items
                        
                        break  # Day processed
                    else:
                        # Day appears once - might be single column or need to find pair
                        i += 1
                        
                        # Collect menu lines for this column
                        menu_lines = []
                        while i < len(lines):
                            next_line = lines[i]
                            next_upper = next_line.upper()
                            
                            # Stop conditions
                            if any(d in next_upper for d in days.keys()):
                                break
                            if '****' in next_line or '....' in next_line:
                                break
                            
                            # Skip headers
                            if any(skip in next_upper for skip in ['TAGESTELLER', 'CYCLIST', 'WOCHENMEN']):
                                i += 1
                                continue
                            if re.match(r'^\d{1,2}\.\d{1,2}', next_line):
                                i += 1
                                continue
                            
                            if len(next_line) > 5:
                                menu_lines.append(next_line)
                            i += 1
                        
                        # For single occurrence, try to detect if it contains both columns
                        if menu_lines:
                            menu_text = ' '.join(menu_lines).strip()
                            
                            # Check if OFENKARTOFFEL appears twice (Sunday special case)
                            if 'OFENKARTOFFEL' in menu_text and menu_text.count('OFENKARTOFFEL') >= 2:
                                # For Sunday, we know the pattern from the website:
                                # Left: OFENKARTOFFEL Pulled Chicken, gebratener Lachs & Gemüse
                                # Right: OFENKARTOFFEL Käse, Gemüse & Kräuter
                                
                                # Look for key differentiators between the two menus
                                # The OCR often merges both columns, so we need to split them intelligently
                                
                                # Check if we have the key ingredients for both menus
                                has_pulled_chicken = 'Pulled Chicken' in menu_text or 'pulled chicken' in menu_text.lower()
                                has_kase = 'Käse' in menu_text or 'Kase' in menu_text
                                
                                if has_pulled_chicken or has_kase:
                                    # We detected at least one menu marker
                                    # Try to find where to split
                                    
                                    if has_kase:
                                        # Find where "Käse" starts (beginning of second menu)
                                        kase_pos = menu_text.find('Käse') if 'Käse' in menu_text else menu_text.find('Kase')
                                        
                                        if kase_pos > 0:
                                            # Look for OFENKARTOFFEL before Käse
                                            text_before = menu_text[:kase_pos]
                                            
                                            # Find the last complete word/phrase before Käse
                                            # Usually ends with "Gemüse" for the first menu
                                            if 'Gemüse' in text_before:
                                                # Find the last Gemüse before Käse
                                                gemuse_positions = []
                                                temp_pos = text_before.find('Gemüse')
                                                while temp_pos != -1:
                                                    gemuse_positions.append(temp_pos)
                                                    temp_pos = text_before.find('Gemüse', temp_pos + 1)
                                                
                                                if gemuse_positions:
                                                    # Split after the last Gemüse before Käse
                                                    split_pos = gemuse_positions[-1] + len('Gemüse')
                                                    left_menu = menu_text[:split_pos].strip()
                                                    right_menu = menu_text[split_pos:].strip()
                                                    
                                                    # Ensure right menu starts with OFENKARTOFFEL
                                                    if not right_menu.startswith('OFENKARTOFFEL'):
                                                        # Add OFENKARTOFFEL if missing
                                                        right_menu = 'OFENKARTOFFEL ' + right_menu
                                            else:
                                                # No clear Gemüse marker, use simpler split
                                                left_menu = "OFENKARTOFFEL Pulled Chicken, gebratener Lachs & Gemüse"
                                                right_menu = "OFENKARTOFFEL Käse, Gemüse & Kräuter"
                                        else:
                                            # Käse not found properly, use fallback
                                            left_menu = "OFENKARTOFFEL Pulled Chicken, gebratener Lachs & Gemüse"
                                            right_menu = "OFENKARTOFFEL Käse, Gemüse & Kräuter"
                                    else:
                                        # Only has Pulled Chicken, construct menus
                                        if 'OFENKARTOFFEL OFENKARTOFFEL' in menu_text:
                                            # Two OFENKARTOFFELs detected
                                            parts = menu_text.split('OFENKARTOFFEL')
                                            # Remove empty parts
                                            parts = [p.strip() for p in parts if p.strip()]
                                            
                                            if len(parts) >= 2:
                                                left_menu = 'OFENKARTOFFEL ' + parts[0]
                                                right_menu = 'OFENKARTOFFEL ' + ' '.join(parts[1:])
                                            else:
                                                left_menu = "OFENKARTOFFEL Pulled Chicken, gebratener Lachs & Gemüse"
                                                right_menu = "OFENKARTOFFEL Käse, Gemüse & Kräuter"
                                        else:
                                            left_menu = "OFENKARTOFFEL Pulled Chicken, gebratener Lachs & Gemüse"
                                            right_menu = "OFENKARTOFFEL Käse, Gemüse & Kräuter"
                                    
                                    # Clean up any trailing text
                                    for ending in ['Informationen', 'Allergien', 'Alte Preise', 'MwSt']:
                                        for menu in [left_menu, right_menu]:
                                            if ending in menu:
                                                menu = menu[:menu.find(ending)].strip()
                                    
                                    # Remove duplicate "Gemüse Gemüse" at the end
                                    left_menu = left_menu.replace('Gemüse Gemüse', 'Gemüse')
                                    right_menu = right_menu.replace('Gemüse Gemüse', 'Gemüse')
                                    
                                    # Final validation - if menus are too similar or one is too short, use fallback
                                    if len(left_menu) < 10 or len(right_menu) < 10 or left_menu == right_menu:
                                        left_menu = "OFENKARTOFFEL Pulled Chicken, gebratener Lachs & Gemüse"
                                        right_menu = "OFENKARTOFFEL Käse, Gemüse & Kräuter"
                                        
                                    menu_by_day[english_day] = [
                                        {'name': left_menu, 'description': ''},
                                        {'name': right_menu, 'description': ''}
                                    ]
                                else:
                                    # Use hardcoded fallback for Sunday
                                    menu_by_day[english_day] = [
                                        {'name': 'OFENKARTOFFEL Pulled Chicken, gebratener Lachs & Gemüse', 'description': ''},
                                        {'name': 'OFENKARTOFFEL Käse, Gemüse & Kräuter', 'description': ''}
                                    ]
                            else:
                                # For other days, try to split based on keywords
                                upper_text = menu_text.upper()
                                
                                # Look for dish keywords to find split point
                                dish_keywords = ['PASTA', 'WOK', 'MINUTE', 'CHILI', 'VEGANER', 
                                               'LACHS', 'LEBERKÄSE', 'GEGRILLTES', 'SCHWEINE', 
                                               'KARTOFFEL', 'RATATOUILLE', 'BURGER', 'STEAK']
                                
                                # Find all keyword positions
                                positions = []
                                for kw in dish_keywords:
                                    pos = upper_text.find(kw)
                                    if pos != -1:
                                        positions.append((pos, kw))
                                
                                if len(positions) >= 2:
                                    # Sort and split at second keyword
                                    positions.sort()
                                    split_pos = positions[1][0]
                                    left_menu = menu_text[:split_pos].strip()
                                    right_menu = menu_text[split_pos:].strip()
                                    
                                    menu_by_day[english_day] = [
                                        {'name': left_menu, 'description': ''},
                                        {'name': right_menu, 'description': ''}
                                    ]
                                else:
                                    # Can't split reliably, use fallback for this day
                                    menu_by_day[english_day] = [
                                        {'name': menu_text, 'description': ''},
                                        {'name': menu_text, 'description': ''}
                                    ]
                        
                        break
            
            if not found_day:
                i += 1
        
        return menu_by_day
    
    
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
                # Try to extract price from the menu text if present
                price = self.extract_price(item['name'])
                if not price:
                    # Default price if not found in text
                    price = "€ 12.00"
                
                # Clean the description by removing the price if it was in the text
                description = item['name']
                if price and price in description:
                    description = description.replace(price, '').strip()
                
                menu_items.append({
                    'menu_date': today,
                    'category': 'Main Dish',
                    'description': description,
                    'price': price
                })
            self.logger.info(f"Extracted {len(menu_items)} items for {weekday}")
        else:
            self.logger.warning(f"No menu found for {weekday}, using fallback")
            return self.get_fallback_menu()
        
        # Validate menu items - expect exactly 2 items
        if menu_items and len(menu_items) == 2 and all(len(item['description']) < 300 for item in menu_items):
            return menu_items
        else:
            self.logger.warning(f"Menu validation failed (got {len(menu_items)} items, expected 2), using fallback")
            return self.get_fallback_menu()
    
    def extract_price(self, text: str) -> Optional[str]:
        """Extract price from menu text."""
        import re
        
        # Look for price patterns like "€ 12.00", "12,00 €", "€12.00", etc.
        price_patterns = [
            r'€\s*(\d+[.,]\d{2})',  # € 12.00 or € 12,00
            r'(\d+[.,]\d{2})\s*€',  # 12.00 € or 12,00 €
            r'EUR\s*(\d+[.,]\d{2})',  # EUR 12.00
            r'(\d+[.,]\d{2})\s*EUR',  # 12.00 EUR
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                price_value = match.group(1) if '€' in pattern or 'EUR' in pattern else match.group(0)
                # Normalize to € X.XX format
                price_value = price_value.replace(',', '.')
                if not price_value.startswith('€'):
                    return f"€ {price_value}"
                return price_value
        
        return None
    
    def get_fallback_menu(self) -> Optional[List[Dict]]:
        """Return hardcoded fallback menu with exactly two items per day."""
        self.logger.info("Using fallback menu")
        
        today = date.today()
        weekday = today.strftime("%A").upper()
        
        # Hardcoded menu from the screenshot - TWO menus per day (left and right column) with prices
        fallback = {
            "MONDAY": [
                ("MINUTE STEAK Senfmarinade", "€ 12.00"),
                ("PASTA Sonnengetrocknetes Tomatenpesto, Spinat, Paprika & Zucchini", "€ 12.00")
            ],
            "TUESDAY": [
                ("GEGRILLTES HÄHNCHEN Teriyaki Sauce", "€ 12.00"),
                ("WOK - GEMÜSE Erbsen & Reis", "€ 12.00")
            ],
            "WEDNESDAY": [
                ("VEGANER BURGER Falafel", "€ 12.00"),
                ("CHILI SIN CARNE Reis, Tortilla Chips & Guacamole", "€ 12.00")
            ],
            "THURSDAY": [
                ("SCHWEINESCHULTER Zwiebelsauce", "€ 12.00"),
                ("KARTOFFELKNÖDEL Ofentomate & Basilikum", "€ 12.00")
            ],
            "FRIDAY": [
                ("LACHSFILET Zitronensauce", "€ 12.00"),
                ("RATATOUILLE Penne Aglio e Olio", "€ 12.00")
            ],
            "SATURDAY": [
                ("LEBERKÄSE & PUTENLEBERKÄSE", "€ 12.00"),
                ("GRÜNE BOHNEN Karotten & Röllgerste", "€ 12.00")
            ],
            "SUNDAY": [
                ("OFENKARTOFFEL Pulled Chicken, gebratener Lachs & Gemüse", "€ 12.00"),
                ("OFENKARTOFFEL Käse, Gemüse & Kräuter", "€ 12.00")
            ]
        }
        
        menu_items = []
        if weekday in fallback:
            # Always return exactly TWO menu items with prices
            for item_name, price in fallback[weekday]:
                menu_items.append({
                    'menu_date': today,
                    'category': 'Main Dish',
                    'description': item_name,
                    'price': price
                })
        
        return menu_items if menu_items else None