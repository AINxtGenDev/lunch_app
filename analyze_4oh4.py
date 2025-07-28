#!/usr/bin/env python3
"""Analyze 4oh4.at website structure"""

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
    url = "https://4oh4.at/lunch-menu/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save the HTML for inspection
        with open('4oh4_requests.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"HTML saved to 4oh4_requests.html")
        
        # Look for common menu-related elements
        print("\nSearching for menu content...")
        
        # Look for divs with menu-related classes
        menu_divs = soup.find_all('div', class_=lambda x: x and ('menu' in x.lower() or 'lunch' in x.lower()) if isinstance(x, str) else False)
        print(f"Found {len(menu_divs)} divs with menu-related classes")
        
        # Look for any text containing menu items
        all_text = soup.get_text()
        if 'menu' in all_text.lower() or 'lunch' in all_text.lower():
            print("Found menu-related text in the page")
            
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
        url = "https://4oh4.at/lunch-menu/"
        print(f"Loading {url}")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Additional wait for dynamic content
        time.sleep(3)
        
        # Get the page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Save the rendered HTML
        with open('4oh4_selenium.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"Rendered HTML saved to 4oh4_selenium.html")
        
        # Look for menu content
        print("\nAnalyzing page structure...")
        
        # Check for iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframes")
        
        # Look for specific menu containers
        menu_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='menu'], [class*='lunch'], [id*='menu'], [id*='lunch']")
        print(f"Found {len(menu_elements)} elements with menu-related classes/ids")
        
        # Print some sample text
        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = body_text.split('\n')
        print(f"\nFirst 20 lines of visible text:")
        for i, line in enumerate(lines[:20]):
            if line.strip():
                print(f"  {i}: {line.strip()}")
                
    except Exception as e:
        print(f"Error with Selenium: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    analyze_with_requests()
    analyze_with_selenium()