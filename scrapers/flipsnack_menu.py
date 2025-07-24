# scrapers/flipsnack_menu.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import PyPDF2
import requests
import io
import re
from .base_scraper import BaseScraper

class FlipsnackMenuScraper(BaseScraper):
    def __init__(self):
        super().__init__("Weekly Menu", "https://www.flipsnack.com/EE9BE6CC5A8/wochenmen-14-20-08-2023.html")
    
    def scrape(self):
        """
        Two approaches for Flipsnack:
        1. Use Selenium to extract text from the embedded viewer
        2. Find and download the source PDF directly
        """
        try:
            # Option 1: Selenium approach
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            driver.get(self.url)
            
            # Wait for Flipsnack to load
            wait = WebDriverWait(driver, 20)
            
            # Try to find PDF download link or extract text
            # Flipsnack often has a download button
            try:
                download_btn = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "fs-download-btn"))
                )
                pdf_url = download_btn.get_attribute('href')
                
                # Download and parse PDF
                return self._parse_pdf_from_url(pdf_url)
                
            except:
                # Fallback: Try to extract visible text from pages
                return self._extract_from_flipsnack_viewer(driver)
                
        except Exception as e:
            self.logger.error(f"Flipsnack scraping failed: {e}")
            return None
        finally:
            if 'driver' in locals():
                driver.quit()
    
    def _parse_pdf_from_url(self, pdf_url):
        """Download and parse PDF content"""
        response = requests.get(pdf_url)
        pdf_file = io.BytesIO(response.content)
        
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        menu_data = {
            'date': datetime.now().date(),
            'items': {}
        }
        
        # Extract text from each page
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            # Parse daily menus from text
            daily_menus = self._parse_menu_text(text)
            menu_data['items'].update(daily_menus)
        
        return menu_data
    
    def _parse_menu_text(self, text):
        """Parse menu items from PDF text"""
        # This will need customization based on PDF structure
        # Example pattern matching for daily menus
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        menus = {}
        
        for day in days:
            # Find menu sections for each day
            day_pattern = rf'{day}.*?(?={"|".join(days)}|$)'
            day_match = re.search(day_pattern, text, re.DOTALL | re.IGNORECASE)
            
            if day_match:
                day_text = day_match.group()
                menus[day.lower()] = self._extract_dishes_from_text(day_text)
        
        return menus