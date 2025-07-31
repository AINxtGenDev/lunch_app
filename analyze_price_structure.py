#!/usr/bin/env python3
"""Analyze how prices are structured on the Erste Campus website."""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def get_chrome_driver():
    """Set up Chrome driver with appropriate options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def analyze_price_structure():
    """Analyze how prices are displayed on the page."""
    driver = None
    try:
        driver = get_chrome_driver()
        url = "https://erstecampus.at/mealplan/2025/external/single/kantine-en.html"
        print(f"Loading: {url}")
        driver.get(url)
        
        # Wait for content to load
        time.sleep(5)
        
        # Get all text content
        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = body_text.split('\n')
        
        print("\n=== ANALYZING PRICE PATTERNS ===\n")
        
        # Look for price patterns
        price_pattern = re.compile(r'€\s*\d+[,.\d]*')
        
        for i, line in enumerate(lines):
            if price_pattern.search(line):
                print(f"Line {i}: {line}")
                # Show context (2 lines before and after)
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    if j != i:
                        print(f"  [{j}]: {lines[j]}")
                print("-" * 50)
        
        # Try to find main dish sections
        print("\n=== MAIN DISH SECTIONS ===\n")
        
        in_main_dish = False
        for i, line in enumerate(lines):
            if "MAIN DISH" in line.upper() or "HAUPTSPEISE" in line.upper():
                in_main_dish = True
                print(f"\n--- Found MAIN DISH at line {i} ---")
                # Print next 20 lines to see structure
                for j in range(i, min(len(lines), i+20)):
                    print(f"[{j}]: {lines[j]}")
                in_main_dish = False
                
        # Look for specific elements with prices
        print("\n=== CHECKING HTML ELEMENTS ===\n")
        
        # Try different selectors
        selectors = [
            ("div.price", "Price divs"),
            ("span.price", "Price spans"),
            ("[class*='price']", "Elements with 'price' in class"),
            ("div:has(> span:contains('€'))", "Divs containing € symbol"),
            ("*:contains('€')", "All elements with € symbol")
        ]
        
        for selector, description in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"\n{description}: Found {len(elements)} elements")
                    for elem in elements[:5]:  # Show first 5
                        print(f"  Text: {elem.text}")
                        print(f"  HTML: {elem.get_attribute('outerHTML')[:200]}...")
            except:
                # Some selectors might not work
                pass
        
        # Get page source for manual inspection
        page_source = driver.page_source
        
        # Look for price patterns in HTML
        print("\n=== PRICE PATTERNS IN HTML ===\n")
        price_html_pattern = re.compile(r'(€\s*\d+[,.\d]*)', re.IGNORECASE)
        matches = price_html_pattern.findall(page_source)
        unique_prices = list(set(matches))
        print(f"Unique prices found: {unique_prices}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    analyze_price_structure()