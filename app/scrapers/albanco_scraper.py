"""
Albanco restaurant scraper implementation.
Extracts weekly lunch menu from PDF at albanco.at
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import requests
import re
import PyPDF2
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
                
                logger.debug(f"Extracted PDF text (first 500 chars): {text[:500]}")
                
                # Parse the menu items from text
                menu_items = self._parse_menu_text(text)
                
        except Exception as e:
            logger.error(f"Error extracting menu from PDF: {str(e)}", exc_info=True)
            raise
        
        return menu_items
    
    def _parse_menu_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse menu items from PDF text.
        
        Expected format:
        DISH NAME (allergens) price
        German description
        English description
        """
        menu_items = []
        today = datetime.now().date()
        
        # Split text into lines and clean up
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for dish pattern: NAME (allergens) price
            # Price pattern: decimal number at end of line
            price_match = re.search(r'(\d+[,\.]\d+)\s*$', line)
            
            if price_match and '(' in line:
                # Extract dish name and price
                price_str = price_match.group(1).replace(',', '.')
                price = f"€ {price_str}"
                
                # Extract dish name (everything before allergens)
                allergen_start = line.rfind('(')
                if allergen_start > 0:
                    dish_name = line[:allergen_start].strip()
                    
                    # Skip very short names (likely parsing errors)
                    if len(dish_name) < 3:
                        i += 1
                        continue
                    
                    # Look for description in next 1-3 lines
                    description_parts = []
                    j = i + 1
                    
                    # Collect description lines (stop at next dish or end)
                    while j < len(lines) and j < i + 4:
                        next_line = lines[j]
                        
                        # Stop if we hit another dish (contains price pattern)
                        if re.search(r'(\d+[,\.]\d+)\s*$', next_line) and '(' in next_line:
                            break
                        
                        # Add description line if it's meaningful
                        if len(next_line) > 5 and not re.match(r'^[A-Z\s]+$', next_line):
                            description_parts.append(next_line)
                        
                        j += 1
                    
                    # Combine descriptions
                    description = ' | '.join(description_parts) if description_parts else dish_name
                    
                    # Determine category based on dish name
                    category = self._categorize_dish(dish_name)
                    
                    # Clean up description (remove duplicates, limit length)
                    if len(description) > 200:
                        description = description[:200] + "..."
                    
                    menu_items.append({
                        'menu_date': today,
                        'category': category,
                        'description': f"{dish_name} - {description}",
                        'price': price
                    })
                    
                    logger.debug(f"Added item: {dish_name} - {price}")
                    
                    # Move to after the description
                    i = j
                else:
                    i += 1
            else:
                i += 1
        
        logger.info(f"Parsed {len(menu_items)} menu items from Albanco PDF")
        return menu_items
    
    def _categorize_dish(self, dish_name: str) -> str:
        """Categorize dish based on name."""
        dish_lower = dish_name.lower()
        
        if any(word in dish_lower for word in ['insalata', 'salat', 'salad']):
            return "Salad"
        elif any(word in dish_lower for word in ['pasta', 'penne', 'spaghetti', 'linguine', 'cannelloni']):
            return "Pasta"
        elif any(word in dish_lower for word in ['risotto']):
            return "Risotto"
        elif any(word in dish_lower for word in ['hamburger', 'burger']):
            return "Burger"
        elif any(word in dish_lower for word in ['pizza']):
            return "Pizza"
        elif any(word in dish_lower for word in ['zuppa', 'suppe', 'soup']):
            return "Soup"
        elif any(word in dish_lower for word in ['dolce', 'dessert', 'tiramisu']):
            return "Dessert"
        else:
            return "Main Dish"
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method required by BaseScraper.
        """
        return self.extract_menu_items()