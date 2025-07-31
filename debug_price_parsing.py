#!/usr/bin/env python3
"""Debug the price parsing logic."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.scrapers.chrome_driver_setup import get_chrome_driver
from selenium.webdriver.common.by import By
import time
import re

def debug_parsing():
    """Debug how the parser handles the menu structure."""
    driver = None
    try:
        driver = get_chrome_driver()
        url = "https://erstecampus.at/mealplan/2025/external/single/kantine-en.html"
        driver.get(url)
        time.sleep(5)
        
        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = [line.strip() for line in body_text.split('\n') if line.strip()]
        
        print("=== DEBUGGING MAIN DISH PARSING ===\n")
        
        allergen_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L', 'M', 'N', 'O', 'P', 'R']
        
        def is_allergen_line(line):
            """Check if line contains only allergen codes."""
            chars = line.replace(' ', '')
            return len(chars) > 0 and all(c in allergen_codes for c in chars)
        
        i = 0
        main_dish_count = 0
        
        while i < len(lines):
            if lines[i] == 'MAIN DISH':
                main_dish_count += 1
                print(f"\n--- MAIN DISH #{main_dish_count} at line {i} ---")
                i += 1
                
                # Show next 10 lines with analysis
                for j in range(i, min(len(lines), i + 10)):
                    line = lines[j]
                    line_type = "UNKNOWN"
                    
                    if re.match(r'^€\s*\d+', line):
                        line_type = "PRICE"
                    elif is_allergen_line(line):
                        line_type = "ALLERGEN"
                    elif line in ['SOUP', 'MAIN DISH', 'DESSERTS', 'SALAD']:
                        line_type = "CATEGORY"
                    else:
                        line_type = "DESCRIPTION"
                    
                    print(f"  [{j:3d}] ({line_type:12s}): {line}")
            else:
                i += 1
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    debug_parsing()