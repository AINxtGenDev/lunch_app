#!/usr/bin/env python3
"""Simple analysis of price structure using existing chrome driver setup."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.scrapers.chrome_driver_setup import get_chrome_driver
from selenium.webdriver.common.by import By
import time
import re

def analyze_prices():
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
        lines = [line.strip() for line in body_text.split('\n') if line.strip()]
        
        print("\n=== FULL PAGE TEXT (first 100 lines) ===\n")
        for i, line in enumerate(lines[:100]):
            print(f"[{i:3d}]: {line}")
        
        print("\n=== LOOKING FOR MAIN DISH SECTIONS ===\n")
        
        # Find main dish sections and their prices
        for i, line in enumerate(lines):
            if "HAUPTSPEISE" in line or "MAIN DISH" in line:
                print(f"\nFound {line} at line {i}")
                print("Next 15 lines:")
                for j in range(i+1, min(len(lines), i+16)):
                    print(f"  [{j:3d}]: {lines[j]}")
                    # Check if this line contains a price
                    if re.search(r'€\s*\d+', lines[j]):
                        print(f"       ^^^ PRICE FOUND!")
        
        print("\n=== PRICE PATTERNS ===\n")
        # Find all lines with prices
        price_lines = []
        for i, line in enumerate(lines):
            if re.search(r'€\s*\d+', line):
                price_lines.append((i, line))
                
        print(f"Found {len(price_lines)} lines with prices:")
        for i, line in price_lines[:20]:  # Show first 20
            print(f"[{i:3d}]: {line}")
            # Show context
            if i > 0:
                print(f"       Previous: {lines[i-1]}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    analyze_prices()