#!/usr/bin/env python3
"""
Debug script to see what content is being extracted from Cyclist menu.
"""

import sys
import time
from datetime import date

sys.path.insert(0, '/home/nuc8/tmp/02_lunch_app/lunch_app')

from app.scrapers.chrome_driver_setup import get_chrome_driver
from selenium.webdriver.common.by import By

def debug_extract():
    driver = None
    try:
        driver = get_chrome_driver()
        url = "https://www.flipsnack.com/EE9BE6CC5A8/wochenmen-14-20-08-2023/full-view.html"
        print(f"Loading: {url}")
        driver.get(url)
        
        time.sleep(8)
        
        # Try to switch to iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframe(s)")
        
        if iframes:
            driver.switch_to.frame(iframes[0])
            print("Switched to iframe")
            time.sleep(3)
        
        # Extract text
        text = driver.execute_script("return document.body.innerText || document.body.textContent || '';")
        
        print(f"\nExtracted {len(text)} characters")
        print("\n" + "="*60)
        print("FULL CONTENT:")
        print("="*60)
        print(text)
        
        # Save to file for analysis
        with open("cyclist_menu_content.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("\n" + "="*60)
        print("Content saved to cyclist_menu_content.txt")
        
        # Look for Wednesday content
        lines = text.split('\n')
        print("\n" + "="*60)
        print("SEARCHING FOR MITTWOCH (Wednesday):")
        print("="*60)
        
        for i, line in enumerate(lines):
            if "MITTWOCH" in line.upper():
                print(f"Found MITTWOCH at line {i}: {line}")
                # Print surrounding lines
                print("\nContext (5 lines before and after):")
                for j in range(max(0, i-5), min(len(lines), i+10)):
                    prefix = ">>> " if j == i else "    "
                    print(f"{prefix}Line {j}: {lines[j]}")
                print()
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    debug_extract()