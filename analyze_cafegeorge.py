#!/usr/bin/env python3
"""Analyze cafegeorge.at website structure"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def analyze_with_requests():
    """Try to fetch the page with requests first"""
    print("=== Analyzing with requests ===")
    url = "https://cafegeorge.at/en/weekly-menu-en/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save the HTML for inspection
        with open('cafegeorge_requests.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"HTML saved to cafegeorge_requests.html")
        
        # Look for menu-related elements
        print("\nSearching for menu content...")
        
        # Look for common menu-related patterns
        menu_keywords = ['menu', 'weekly', 'lunch', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        
        for keyword in menu_keywords:
            elements = soup.find_all(text=lambda text: text and keyword.lower() in text.lower())
            if elements:
                print(f"Found {len(elements)} elements containing '{keyword}'")
        
        # Look for price elements
        price_elements = soup.find_all(text=lambda text: text and ('€' in text or 'EUR' in text))
        print(f"\nFound {len(price_elements)} elements with prices")
        for elem in price_elements[:10]:
            print(f"  - {elem.strip()}")
            
    except Exception as e:
        print(f"Error with requests: {e}")

def analyze_with_selenium():
    """Use Selenium to render JavaScript content"""
    print("\n=== Analyzing with Selenium ===")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        url = "https://cafegeorge.at/en/weekly-menu-en/"
        print(f"Loading {url}")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Additional wait for dynamic content
        time.sleep(5)
        
        # Get the page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Save the rendered HTML
        with open('cafegeorge_selenium.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"Rendered HTML saved to cafegeorge_selenium.html")
        
        # Look for menu content
        print("\nAnalyzing page structure...")
        
        # Look for elements with menu-related classes
        menu_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='menu'], [class*='weekly'], [class*='lunch'], [id*='menu']")
        print(f"Found {len(menu_elements)} elements with menu-related classes/ids")
        
        # Look for table structures (often used for weekly menus)
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"Found {len(tables)} tables")
        
        # Look for day-based structures
        day_keywords = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag']
        
        for keyword in day_keywords:
            elements = driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]")
            if elements:
                print(f"Found {len(elements)} elements containing '{keyword}'")
        
        # Look for specific content patterns
        print("\nLooking for content patterns...")
        
        # Check for iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframes")
        
        # Print some sample text
        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = body_text.split('\n')
        print(f"\nFirst 50 lines of visible text:")
        for i, line in enumerate(lines[:50]):
            if line.strip():
                print(f"  {i}: {line.strip()}")
                
    except Exception as e:
        print(f"Error with Selenium: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    analyze_with_requests()
    analyze_with_selenium()