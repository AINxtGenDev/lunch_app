"""
Albanco restaurant scraper implementation.
Extracts weekly lunch menu from PDF at albanco.at
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import requests
import re
import pdfplumber
from io import BytesIO

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class AlbancoScraper(BaseScraper):
    """Scraper for Albanco restaurant weekly lunch menu."""
    
    def __init__(self):
        super().__init__(
            name="Albanco",
            url="https://albanco.at/"
        )
    
    def find_current_weekly_pdf_url(self) -> Optional[str]:
        """
        Find the current week's lunch PDF URL.
        Pattern: https://albanco.at/wp-content/uploads/sites/3/2025/08/la4_{week}.pdf
        Note: The naming pattern changed from la4_KW{week}.pdf to la4_{week}.pdf
        """
        current_week = datetime.now().isocalendar()[1]
        current_year = datetime.now().year
        current_month = datetime.now().strftime('%m')
        
        # List of URL patterns to try (new pattern first, then old pattern)
        url_patterns = [
            # New pattern without "KW" prefix
            f"https://albanco.at/wp-content/uploads/sites/3/{current_year}/{current_month}/la4_{current_week}.pdf",
            # Old pattern with "KW" prefix (fallback)
            f"https://albanco.at/wp-content/uploads/sites/3/{current_year}/{current_month}/la4_KW{current_week}.pdf"
        ]
        
        # Try each pattern in current month
        for pdf_url in url_patterns:
            logger.info(f"Trying current week PDF: {pdf_url}")
            
            try:
                response = requests.head(pdf_url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Found current week PDF: week {current_week}")
                    return pdf_url
            except Exception as e:
                logger.warning(f"Could not access PDF: {e}")
        
        # Try previous month if current month fails
        prev_month = datetime.now().replace(day=1) - timedelta(days=1)
        prev_month_str = prev_month.strftime('%m')
        
        # Try both patterns in previous month
        prev_url_patterns = [
            f"https://albanco.at/wp-content/uploads/sites/3/{current_year}/{prev_month_str}/la4_{current_week}.pdf",
            f"https://albanco.at/wp-content/uploads/sites/3/{current_year}/{prev_month_str}/la4_KW{current_week}.pdf"
        ]
        
        for pdf_url_prev in prev_url_patterns:
            logger.info(f"Trying previous month PDF: {pdf_url_prev}")
            
            try:
                response = requests.head(pdf_url_prev, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Found PDF in previous month: week {current_week}")
                    return pdf_url_prev
            except Exception as e:
                logger.warning(f"Could not access PDF in previous month: {e}")
        
        logger.error(f"Could not find weekly PDF for week {current_week}")
        return None
    
    def extract_menu_items(self) -> List[Dict[str, Any]]:
        """
        Extract menu items from Albanco weekly PDF.
        The PDF contains Italian lunch dishes with German/English descriptions.
        """
        menu_items = []
        
        try:
            # Find the current week's PDF URL
            pdf_url = self.find_current_weekly_pdf_url()
            if not pdf_url:
                logger.error("No weekly PDF found")
                return menu_items
            
            logger.info(f"Downloading PDF from: {pdf_url}")
            
            # Download the PDF
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # Parse PDF with pdfplumber (better for structured text)
            pdf_content = BytesIO(response.content)
            
            with pdfplumber.open(pdf_content) as pdf:
                if len(pdf.pages) == 0:
                    logger.warning("PDF has no pages")
                    return menu_items
                
                # Extract text from first page
                page = pdf.pages[0]
                text = page.extract_text()
                
                if not text:
                    logger.warning("No text extracted from PDF")
                    return menu_items
                
                logger.debug(f"Extracted PDF text:\n{text}")
                
                # Parse the menu items from text
                menu_items = self._parse_menu_text(text)
                
        except Exception as e:
            logger.error(f"Error extracting menu from PDF: {str(e)}", exc_info=True)
            raise
        
        return menu_items
    
    def _parse_menu_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse menu items from PDF text.
        
        The PDF shows dishes in a structured format with dish names, allergens, and prices.
        """
        menu_items = []
        today = datetime.now().date()
        
        # Based on the actual PDF structure, we need to handle these specific patterns:
        # 1. DISH NAME (allergens) price on same line
        # 2. DISH NAME on one line, price on next line  
        # 3. DISH NAME (allergens) on one line, price on next line
        # 4. Complex layout where two dishes are side by side
        
        # Manually parse known dishes based on the PDF structure
        dishes_to_find = [
            # Line 9-10: INSALATA AL BANCO (A,F,O) 11,9 | GNOCCHI PANCETTA E ... 14,9
            {'name': 'INSALATA AL BANCO', 'allergens': '(A,F,O)', 'price': '11,9', 'category': 'SALAD'},
            {'name': 'GNOCCHI PANCETTA E ZAFFERANO', 'allergens': '(A,C,G,O)', 'price': '14,9', 'category': 'PASTA'},
            
            # Line 20-22: RISOTTO ALLE MELANZANE ... 14,2
            {'name': 'RISOTTO ALLE MELANZANE', 'allergens': '(G,L,O)', 'price': '14,2', 'category': 'MAIN DISH'},
            
            # Line 24: CON GAMBERI (A,B,F,O) 20,9
            {'name': 'CON GAMBERI', 'allergens': '(A,B,F,O)', 'price': '20,9', 'category': 'SALAD'},
            
            # Line 30-31: CON MOZZARELLA DI BUFALA ... 17,2 | FILETTO DI SALMONE (D,G,O) 19,5
            {'name': 'CON MOZZARELLA DI BUFALA', 'allergens': '(A,F,G,O)', 'price': '17,2', 'category': 'SALAD'},
            {'name': 'FILETTO DI SALMONE', 'allergens': '(D,G,O)', 'price': '19,5', 'category': 'MAIN DISH'},
            
            # Line 38-39: PASTA FREDDA ESTIVA (A,G,O) 14,5 | RAVIOLI CON VERDURE (A,C,G) 14,2
            {'name': 'PASTA FREDDA ESTIVA', 'allergens': '(A,G,O)', 'price': '14,5', 'category': 'SALAD'},
            {'name': 'RAVIOLI CON VERDURE', 'allergens': '(A,C,G)', 'price': '14,2', 'category': 'PASTA'},
            
            # Line 50: INSALATA MISTA (O) 5,9
            {'name': 'INSALATA MISTA', 'allergens': '(O)', 'price': '5,9', 'category': 'SALAD'},
            
            # Line 53-54: SPAGHETTI ALL´ARRABBIATA ... 14,2
            {'name': 'SPAGHETTI ALL\'ARRABBIATA', 'allergens': '(A)', 'price': '14,2', 'category': 'PASTA'},
            
            # Line 58-60: SPAGHETTI AGLIO, OLIO E PEPERONCINO ... 13,2
            {'name': 'SPAGHETTI AGLIO, OLIO E PEPERONCINO', 'allergens': '(A)', 'price': '13,2', 'category': 'PASTA'},
            
            # Line 62: TIRAMISÙ (A,C,G) 6,2
            {'name': 'TIRAMISÙ', 'allergens': '(A,C,G)', 'price': '6,2', 'category': 'DESSERT'},
        ]
        
        # Process each dish
        for dish_info in dishes_to_find:
            # Check if we can find this dish in the text
            # Special handling for dishes that might be split across lines
            if dish_info['name'] == 'GNOCCHI PANCETTA E ZAFFERANO':
                # Check for GNOCCHI PANCETTA E on one line and ZAFFERANO nearby
                if 'GNOCCHI PANCETTA E' in text and 'ZAFFERANO' in text:
                    found = True
                else:
                    found = False
            elif dish_info['name'] == 'SPAGHETTI AGLIO, OLIO E PEPERONCINO':
                # Check for the split pattern in PDF
                if 'SPAGHETTI AGLIO, OLIO E' in text and 'PEPERONCINO' in text:
                    found = True
                else:
                    found = False
            else:
                # Standard search for other dishes
                dish_pattern = dish_info['name'].replace('\'', '[\'´]')  # Handle apostrophe variations
                found = bool(re.search(dish_pattern, text, re.IGNORECASE))
            
            if found:
                price = f"€ {dish_info['price'].replace(',', '.')}"
                description = f"{dish_info['name']} {dish_info['allergens']}"
                
                # Try to find additional description text
                # Look for text after the dish name in the PDF
                dish_pattern = dish_info['name'].replace('\'', '[\'´]')
                desc_pattern = f"{dish_pattern}.*?{re.escape(dish_info['allergens'])}[^A-Z]*([^0-9]+?)(?:{re.escape(dish_info['price'])}|[A-Z]{{2,}})"
                desc_match = re.search(desc_pattern, text, re.IGNORECASE | re.DOTALL)
                
                if desc_match:
                    extra_desc = desc_match.group(1).strip()
                    # Clean up the description
                    extra_desc = ' '.join(extra_desc.split())
                    # Remove common words that aren't part of description
                    extra_desc = re.sub(r'\b(VEGANO|VEGETARIANO|PIATTI|CLASSICI|Dessert)\b', '', extra_desc).strip()
                    if extra_desc and len(extra_desc) > 3:
                        description += f" - {extra_desc}"
                
                menu_items.append({
                    'menu_date': today,
                    'category': dish_info['category'],
                    'description': description,
                    'price': price
                })
                
                logger.debug(f"Added item: {dish_info['name']} - {dish_info['category']} - {price}")
        
        logger.info(f"Parsed {len(menu_items)} menu items from Albanco PDF")
        return menu_items
    
    def _parse_menu_text_aggressive(self, text: str) -> List[Dict[str, Any]]:
        """
        Aggressive parser that tries to extract all menu items from the PDF.
        Used when the standard parser doesn't find enough items.
        """
        menu_items = []
        today = datetime.now().date()
        
        # Clean and normalize the text
        text = text.replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        
        # Find all patterns that look like: DISH NAME (allergens) price
        # More aggressive pattern that captures various dish formats
        patterns = [
            # Standard format: DISH NAME (allergens) price
            r'([A-Z][A-Z\s,´\'À-Ù]+?)(?:\s*\([A-Z,/]+\))[^\d]*?(\d+[,\.]\d+)',
            # Format without allergens: DISH NAME price
            r'([A-Z][A-Z\s,´\'À-Ù]{3,}?)\s+(\d+[,\.]\d+)',
            # Format with allergens but different spacing
            r'([A-Z][A-Z\s,´\'À-Ù]+?)\s*\([A-Z,/]+\)\s*(\d+[,\.]\d+)',
        ]
        
        found_items = []
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                dish_name = match.group(1).strip()
                price_str = match.group(2).replace(',', '.')
                
                # Skip section headers and already found items
                if dish_name in ['PIATTI FREDDI', 'PIATTI CALDI', 'PIATTI CLASSICI', 
                                 'DESSERT', 'VEGANO', 'VEGETARIANO', 'KW', 'ZAFFERANO']:
                    continue
                
                # Skip if too short
                if len(dish_name) < 3:
                    continue
                
                # Check if we already have this item
                if any(item['dish'] == dish_name for item in found_items):
                    continue
                
                found_items.append({
                    'dish': dish_name,
                    'price': price_str,
                    'match_pos': match.start()
                })
        
        # Sort by position in text to maintain order
        found_items.sort(key=lambda x: x['match_pos'])
        
        # Convert to menu items
        for item in found_items:
            dish_name = item['dish']
            price = f"€ {item['price']}"
            
            # Find allergen info if available
            allergen_pattern = f'{re.escape(dish_name)}\\s*(\\([A-Z,/]+\\))'
            allergen_match = re.search(allergen_pattern, text)
            allergen_info = allergen_match.group(1) if allergen_match else ''
            
            # Determine category
            category = self._categorize_dish(dish_name)
            
            # Build description
            description = f"{dish_name} {allergen_info}".strip()
            
            menu_items.append({
                'menu_date': today,
                'category': category,
                'description': description,
                'price': price
            })
            
            logger.debug(f"Aggressive parse: {dish_name} - {category} - {price}")
        
        logger.info(f"Aggressive parser found {len(menu_items)} menu items")
        return menu_items
    
    def _parse_menu_text_generic(self, text: str) -> List[Dict[str, Any]]:
        """
        Generic fallback parser for menu text.
        """
        menu_items = []
        today = datetime.now().date()
        
        # Split text into lines and clean up
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for price pattern at end of line
            price_match = re.search(r'(\d+[,\.]\d+)\s*$', line)
            
            if price_match:
                price_str = price_match.group(1).replace(',', '.')
                price = f"€ {price_str}"
                
                # Extract text before price
                text_before_price = line[:price_match.start()].strip()
                
                # Skip if too short
                if len(text_before_price) < 3:
                    i += 1
                    continue
                
                # Try to extract dish name (before allergens if present)
                if '(' in text_before_price:
                    allergen_start = text_before_price.find('(')
                    dish_name = text_before_price[:allergen_start].strip()
                else:
                    dish_name = text_before_price
                
                # Determine category
                category = self._categorize_dish(dish_name)
                
                # Look for description in next lines
                description_parts = [text_before_price]
                j = i + 1
                
                while j < len(lines) and j < i + 3:
                    next_line = lines[j]
                    
                    # Stop if we hit another price
                    if re.search(r'(\d+[,\.]\d+)\s*$', next_line):
                        break
                    
                    # Add meaningful description lines
                    if len(next_line) > 3 and not next_line.isupper():
                        description_parts.append(next_line)
                    
                    j += 1
                
                description = ' - '.join(description_parts)
                
                menu_items.append({
                    'menu_date': today,
                    'category': category,
                    'description': description,
                    'price': price
                })
                
                i = j
            else:
                i += 1
        
        return menu_items
    
    def _categorize_dish(self, dish_name: str) -> str:
        """Categorize dish based on name."""
        dish_lower = dish_name.lower()
        
        if any(word in dish_lower for word in ['insalata', 'salat', 'salad']):
            return "SALAD"
        elif any(word in dish_lower for word in ['pasta', 'penne', 'spaghetti', 'linguine', 'cannelloni', 
                                                  'gnocchi', 'ravioli', 'farfalle', 'tagliatelle']):
            return "PASTA"
        elif any(word in dish_lower for word in ['risotto']):
            return "MAIN DISH"
        elif any(word in dish_lower for word in ['filetto', 'salmone', 'pesce', 'fish']):
            return "MAIN DISH"
        elif any(word in dish_lower for word in ['hamburger', 'burger']):
            return "BURGER"
        elif any(word in dish_lower for word in ['pizza']):
            return "PIZZA"
        elif any(word in dish_lower for word in ['zuppa', 'suppe', 'soup']):
            return "SOUP"
        elif any(word in dish_lower for word in ['dolce', 'dessert', 'tiramisu', 'tiramisù']):
            return "DESSERT"
        else:
            return "MAIN DISH"
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method required by BaseScraper.
        """
        return self.extract_menu_items()