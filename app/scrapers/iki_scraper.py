"""
IKI Restaurant scraper implementation.
Scrapes PDF-based lunch menus from iki-restaurant.at
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
import re

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class IKIScraper(BaseScraper):
    """Scraper for IKI restaurant PDF-based menus."""
    
    def __init__(self):
        super().__init__(
            name="IKI Restaurant",
            url="https://iki-restaurant.at/"
        )
    
    def find_current_lunch_pdf_url(self) -> Optional[str]:
        """
        Find the current week's lunch specials PDF URL.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.url, headers=headers)
            if response.status_code != 200:
                logger.error(f"Failed to load IKI website: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all PDF links
            pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
            
            lunch_pdfs = []
            for link in pdf_links:
                href = link.get('href')
                text = link.get_text(strip=True).lower()
                
                # Look for lunch-related PDFs
                if any(keyword in text for keyword in ['lunch', 'special', 'kw', 'week']):
                    lunch_pdfs.append({
                        'text': link.get_text(strip=True),
                        'url': href
                    })
            
            if not lunch_pdfs:
                logger.warning("No lunch PDFs found")
                return None
            
            # Try to find current week's PDF
            current_week = datetime.now().isocalendar()[1]
            
            for pdf in lunch_pdfs:
                url_text = pdf['url'].lower() + ' ' + pdf['text'].lower()
                
                # Check for current week pattern
                week_match = re.search(r'kw[-\s]*(\d+)', url_text)
                if week_match:
                    pdf_week = int(week_match.group(1))
                    # Allow current week or next week
                    if pdf_week in [current_week, current_week + 1]:
                        logger.info(f"Found current week PDF: {pdf['text']} (KW {pdf_week})")
                        return pdf['url']
            
            # Fallback: use the first lunch PDF
            fallback_pdf = lunch_pdfs[0]
            logger.info(f"Using fallback lunch PDF: {fallback_pdf['text']}")
            return fallback_pdf['url']
            
        except Exception as e:
            logger.error(f"Error finding lunch PDF: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_url: str) -> Optional[str]:
        """
        Extract text from PDF URL.
        """
        try:
            logger.info(f"Downloading PDF from: {pdf_url}")
            response = requests.get(pdf_url)
            
            if response.status_code != 200:
                logger.error(f"Failed to download PDF: {response.status_code}")
                return None
            
            # Try to extract text with PyPDF2
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            full_text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            
            if full_text.strip():
                logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
                return full_text
            else:
                logger.warning("No text could be extracted from PDF")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return None
    
    def parse_menu_items_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse menu items from extracted PDF text.
        """
        menu_items = []
        today = datetime.now().date()
        
        try:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # Look for items with prices (containing €)
                if '€' in line:
                    # Try to extract item name and price
                    price_match = re.search(r'€\s*(\d+[,\.]\d{2})', line)
                    if price_match:
                        price = "€" + price_match.group(1).replace('.', ',')
                        
                        # Extract item name (text before the price)
                        item_name = re.sub(r'€\s*\d+[,\.]\d{2}.*$', '', line).strip()
                        
                        # Clean up item name (remove allergen codes at the end)
                        item_name = re.sub(r'\s+[A-Z]+\s*$', '', item_name).strip()
                        
                        if not item_name:
                            i += 1
                            continue
                        
                        # Determine category based on item name or position
                        category = "Main Dish"
                        item_name_lower = item_name.lower()
                        
                        if any(word in item_name_lower for word in ['bento', 'box']):
                            category = "Bento Box"
                        elif any(word in item_name_lower for word in ['salad', 'salat']):
                            category = "Salad"
                        elif any(word in item_name_lower for word in ['ramen', 'nudeln']):
                            category = "Noodles"
                        elif any(word in item_name_lower for word in ['roll', 'sushi']):
                            category = "Sushi"
                        elif any(word in item_name_lower for word in ['limonade', 'drink']):
                            category = "Beverages"
                        
                        # Check if next line contains description
                        description = ""
                        if i + 1 < len(lines):
                            next_line = lines[i + 1]
                            # If next line doesn't contain price and isn't all caps, it's likely a description
                            if '€' not in next_line and not next_line.isupper() and len(next_line) > 10:
                                description = next_line
                                i += 1  # Skip the description line
                        
                        # Combine name and description
                        full_description = item_name
                        if description:
                            full_description += f" - {description}"
                        
                        menu_items.append({
                            'menu_date': today,
                            'category': category,
                            'description': full_description,
                            'price': price
                        })
                        
                        logger.debug(f"Parsed item: {category} - {full_description} ({price})")
                
                i += 1
            
            logger.info(f"Parsed {len(menu_items)} menu items from PDF text")
            return menu_items
            
        except Exception as e:
            logger.error(f"Error parsing menu items: {e}")
            return []
    
    def extract_menu_items(self) -> List[Dict[str, Any]]:
        """
        Extract menu items from IKI restaurant PDF.
        """
        try:
            # Find current lunch PDF URL
            pdf_url = self.find_current_lunch_pdf_url()
            if not pdf_url:
                logger.error("Could not find current lunch PDF URL")
                return []
            
            # Extract text from PDF
            pdf_text = self.extract_text_from_pdf(pdf_url)
            if not pdf_text:
                logger.error("Could not extract text from PDF")
                return []
            
            # Parse menu items from text
            menu_items = self.parse_menu_items_from_text(pdf_text)
            
            logger.info(f"Successfully extracted {len(menu_items)} menu items from IKI")
            return menu_items
            
        except Exception as e:
            logger.error(f"Error scraping IKI: {str(e)}", exc_info=True)
            return []
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method required by BaseScraper.
        """
        return self.extract_menu_items()