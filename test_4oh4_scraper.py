#!/usr/bin/env python3
"""Test script for 4oh4 scraper with detailed debugging"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from datetime import datetime

def test_4oh4_scraper():
    """Test the 4oh4 scraper with detailed output"""
    driver = None
    
    try:
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize the driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Get the iframe URL directly
        iframe_url = "https://4oh4.at/mealplan/2025/external/single/4oh4.html"
        print(f"Loading iframe URL directly: {iframe_url}")
        
        driver.get(iframe_url)
        
        # Wait for content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Additional wait for dynamic content
        time.sleep(3)
        
        # Get the page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Save the HTML for analysis
        with open('4oh4_iframe_content.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("Saved iframe content to 4oh4_iframe_content.html")
        
        # Analyze the structure
        print("\n=== Page Structure Analysis ===")
        
        # Look for any divs with class or id
        divs_with_class = soup.find_all('div', class_=True)
        print(f"\nFound {len(divs_with_class)} divs with classes")
        
        # Print unique class names
        class_names = set()
        for div in divs_with_class:
            classes = div.get('class', [])
            for cls in classes:
                class_names.add(cls)
        
        print("\nUnique class names found:")
        for cls in sorted(class_names):
            print(f"  - {cls}")
        
        # Look for date elements
        date_elements = soup.find_all(attrs={'data-date': True})
        print(f"\nFound {len(date_elements)} elements with data-date attribute")
        
        # Look for any text containing menu-related keywords
        menu_keywords = ['menu', 'lunch', 'today', 'heute', 'montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag']
        
        print("\n=== Looking for menu content ===")
        for keyword in menu_keywords:
            elements = soup.find_all(text=lambda text: text and keyword.lower() in text.lower())
            if elements:
                print(f"\nFound {len(elements)} elements containing '{keyword}':")
                for elem in elements[:3]:  # Show first 3
                    print(f"  - {elem.strip()[:100]}...")
        
        # Look for structured content
        print("\n=== Looking for structured menu items ===")
        
        # Try different selectors
        selectors = [
            "div.menu-item",
            "div.dish",
            "div.meal",
            "article.menu-item",
            "div[class*='menu']",
            "div[class*='dish']",
            "div[class*='meal']",
            ".menu-content",
            ".daily-menu",
            "[data-menu-item]"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                print(f"\nFound {len(items)} items with selector '{selector}':")
                for item in items[:2]:  # Show first 2
                    text = item.get_text(strip=True)
                    print(f"  - {text[:100]}...")
        
        # Get all text content
        print("\n=== Sample of all text content ===")
        all_text = soup.get_text()
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        
        # Filter for potential menu items
        print("\nPotential menu items (10-150 chars):")
        menu_items = []
        for line in lines:
            if 10 < len(line) < 150:
                # Skip common non-menu text
                skip_words = ['cookie', 'login', 'newsletter', 'contact', 'impressum', 
                             'datenschutz', 'javascript', 'browser', 'privacy']
                if not any(word in line.lower() for word in skip_words):
                    menu_items.append(line)
                    if len(menu_items) <= 20:  # Show first 20
                        print(f"  - {line}")
        
        print(f"\nTotal potential menu items found: {len(menu_items)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_4oh4_scraper()