#!/usr/bin/env python3
"""
Extract raw content from Cyclist menu and save to file.
"""

import sys
import time
from selenium.webdriver.common.by import By

sys.path.insert(0, '/home/nuc8/tmp/02_lunch_app/lunch_app')

from app.scrapers.chrome_driver_setup import get_chrome_driver

def extract_raw():
    driver = None
    try:
        driver = get_chrome_driver()
        url = "https://www.flipsnack.com/EE9BE6CC5A8/wochenmen-14-20-08-2023/full-view.html"
        print(f"Loading: {url}")
        driver.get(url)
        
        print("Waiting for page to load...")
        time.sleep(10)  # Give more time for dynamic content
        
        # Try to switch to iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframe(s)")
        
        if iframes:
            driver.switch_to.frame(iframes[0])
            print("Switched to iframe")
            time.sleep(5)  # More time after switching
        
        # Try multiple extraction methods
        print("\nTrying different extraction methods...")
        
        # Method 1: body.text
        try:
            text1 = driver.find_element(By.TAG_NAME, "body").text
            print(f"Method 1 (body.text): {len(text1)} chars")
            with open("cyclist_raw_method1.txt", "w", encoding="utf-8") as f:
                f.write(text1)
        except Exception as e:
            print(f"Method 1 failed: {e}")
        
        # Method 2: JavaScript innerText
        try:
            text2 = driver.execute_script("return document.body.innerText;")
            print(f"Method 2 (JS innerText): {len(text2) if text2 else 0} chars")
            if text2:
                with open("cyclist_raw_method2.txt", "w", encoding="utf-8") as f:
                    f.write(text2)
        except Exception as e:
            print(f"Method 2 failed: {e}")
        
        # Method 3: All text nodes
        try:
            text3 = driver.execute_script("""
                var text = [];
                var walk = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                var node;
                while(node = walk.nextNode()) {
                    var nodeText = node.textContent.trim();
                    if(nodeText) text.push(nodeText);
                }
                return text.join('\\n');
            """)
            print(f"Method 3 (TreeWalker): {len(text3) if text3 else 0} chars")
            if text3:
                with open("cyclist_raw_method3.txt", "w", encoding="utf-8") as f:
                    f.write(text3)
        except Exception as e:
            print(f"Method 3 failed: {e}")
        
        # Check for specific elements
        print("\nLooking for specific elements...")
        selectors = [
            ".fsBody", ".page-content", ".text-layer", 
            ".flipsnack-page", "[data-page-content]", 
            ".fs-page-content", ".page", ".fsPageContent"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} element(s) with selector: {selector}")
                    for i, elem in enumerate(elements[:3]):  # Check first 3
                        text = elem.text
                        if text:
                            print(f"  Element {i}: {len(text)} chars")
                            print(f"    Preview: {text[:100]}...")
            except:
                pass
        
        print("\nExtraction complete! Check cyclist_raw_*.txt files")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    extract_raw()