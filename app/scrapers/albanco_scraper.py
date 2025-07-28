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
        Pattern: https://albanco.at/wp-content/uploads/sites/3/2025/07/la4_KW{week}.pdf
        """
        current_week = datetime.now().isocalendar()[1]
        current_year = datetime.now().year
        current_month = datetime.now().strftime('%m')
        
        # Try current month first
        pdf_url = f"https://albanco.at/wp-content/uploads/sites/3/{current_year}/{current_month}/la4_KW{current_week}.pdf"
        
        logger.info(f"Trying current week PDF: {pdf_url}")
        
        try:
            response = requests.head(pdf_url, timeout=10)
            if response.status_code == 200:
                logger.info(f"Found current week PDF: KW{current_week}")
                return pdf_url
        except Exception as e:
            logger.warning(f"Could not access PDF for KW{current_week}: {e}")
        
        # Try previous month if current month fails
        prev_month = datetime.now().replace(day=1) - datetime.timedelta(days=1)
        prev_month_str = prev_month.strftime('%m')
        
        pdf_url_prev = f"https://albanco.at/wp-content/uploads/sites/3/{current_year}/{prev_month_str}/la4_KW{current_week}.pdf"
        
        logger.info(f"Trying previous month PDF: {pdf_url_prev}")
        
        try:
            response = requests.head(pdf_url_prev, timeout=10)
            if response.status_code == 200:
                logger.info(f"Found PDF in previous month: KW{current_week}")
                return pdf_url_prev
        except Exception as e:
            logger.warning(f"Could not access PDF in previous month: {e}")
        
        logger.error(f"Could not find weekly PDF for KW{current_week}")
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
        
        # Known menu items from the weekly specials
        # Format: (pattern, category, full_name)
        known_dishes = [
            # PIATTI FREDDI (Cold Dishes)
            (r'INSALATA AL BANCO.*?(\d+[,\.]\d+)', 'SALAD', 'INSALATA AL BANCO (A,F,O) - VEGANO - Salatherzen, Rucola, Kirschtomaten, Avocado, schwarze Oliven, geröstetes Brot'),
            (r'CON GAMBERI.*?(\d+[,\.]\d+)', 'SALAD', 'CON GAMBERI (A,B,F,O) - mit Garnelen | with prawns'),
            (r'CON MOZZARELLA DI BUFALA.*?(\d+[,\.]\d+)', 'SALAD', 'CON MOZZARELLA DI BUFALA (A,F,G,O) - Mit Büffelmozzarella | With Buffalo mozzarella'),
            (r'INSALATA DI PATATE.*?(\d+[,\.]\d+)', 'SALAD', 'INSALATA DI PATATE, FAGIOLINI E TONNO (C,D,O) - Grüne Bohnen, gekochte Kartoffeln, Thunfisch, gekochtes Ei, Cherrytomaten'),
            (r'INSALATA MISTA.*?(\d+[,\.]\d+)', 'SALAD', 'INSALATA MISTA (O) - VEGANO - Beilagensalat | Side dish'),
            
            # PIATTI CALDI (Hot Dishes)
            (r'PENNE AL SALMONE.*?(\d+[,\.]\d+)', 'PASTA', 'PENNE AL SALMONE (A,D,G) - Penne, cremige Räucherlachssauce, Dill | Penne, creamy smoked salmon sauce, dill'),
            (r'RISOTTO CON MIRTILLI E.*?(\d+[,\.]\d+)', 'MAIN DISH', 'RISOTTO CON MIRTILLI E SCAMORZA (G,H,L,O) - Risotto, Heidelbeeren, Scamorza, Pistazien | Risotto, blueberries, scamorza, pistachios'),
            (r'HAMBURGER ITALIANO.*?(\d+[,\.]\d+)', 'BURGER', 'HAMBURGER ITALIANO (A,C,G,N) - Rinderburger, Speck, Scamorza, Basilikum-Mayo, Tomaten, rote Zwiebeln, Rucola, Rosmarinkartoffeln'),
            (r'CANNELLONI AL FORNO.*?(\d+[,\.]\d+)', 'PASTA', 'CANNELLONI AL FORNO (A,G) - Überbackene Ricotta-Cannelloni, Tomatensauce, Mozzarella, Pesto | Baked ricotta-cannelloni'),
            
            # PIATTI CLASSICI (Classic Dishes)
            (r'SPAGHETTI ALL.*?ARRABBIATA.*?(\d+[,\.]\d+)', 'PASTA', 'SPAGHETTI ALL\'ARRABBIATA (A) - VEGANO'),
            (r'SPAGHETTI AGLIO.*?OLIO E.*?PEPERONCINO.*?(\d+[,\.]\d+)', 'PASTA', 'SPAGHETTI AGLIO, OLIO E PEPERONCINO (A) - VEGANO'),
            
            # DESSERT
            (r'TIRAMIS[UÙ].*?(\d+[,\.]\d+)', 'DESSERT', 'TIRAMISÙ (A,C,G) - VEGETARIANO'),
        ]
        
        # Process each known dish pattern
        for pattern, category, full_name in known_dishes:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                price_str = match.group(1).replace(',', '.')
                price = f"€ {price_str}"
                
                # Extract the main dish name (before allergens)
                dish_name_match = re.match(r'([^(]+)', full_name)
                dish_name = dish_name_match.group(1).strip() if dish_name_match else full_name
                
                # Get full description
                description = full_name
                
                menu_items.append({
                    'menu_date': today,
                    'category': category,
                    'description': description,
                    'price': price
                })
                
                logger.debug(f"Added item: {dish_name} - {category} - {price}")
        
        # If we couldn't parse structured items, fall back to generic parsing
        if not menu_items:
            logger.warning("No structured items found, attempting generic parsing")
            return self._parse_menu_text_generic(text)
        
        logger.info(f"Parsed {len(menu_items)} menu items from Albanco PDF")
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
        elif any(word in dish_lower for word in ['pasta', 'penne', 'spaghetti', 'linguine', 'cannelloni']):
            return "PASTA"
        elif any(word in dish_lower for word in ['risotto']):
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