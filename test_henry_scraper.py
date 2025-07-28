#!/usr/bin/env python3
"""Test script for Henry scraper with detailed debugging"""

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

def test_henry_scraper():
    """Test the Henry scraper with detailed output"""
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
        
        url = "https://www.enjoyhenry.com/menuplan-bdo/"
        print(f"Loading Henry menu page: {url}")
        
        driver.get(url)
        
        # Wait for content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Additional wait for dynamic content
        time.sleep(3)
        
        # Get the page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        print("\n=== Looking for today's menu column ===")
        
        # Find the today's menu column
        today_column = soup.find('div', class_='today')
        if not today_column:
            print("ERROR: Could not find today's menu column")
            return
        
        print("✓ Found today's menu column")
        
        # Find all menu items in today's column
        menu_cells = today_column.find_all('div', class_='td-menu')
        print(f"✓ Found {len(menu_cells)} menu cells")
        
        print("\n=== Extracting menu items ===")
        
        menu_items = []
        today = datetime.now().date()
        
        for i, cell in enumerate(menu_cells):
            try:
                print(f"\n--- Processing cell {i+1} ---")
                
                # Extract category
                category_elem = cell.find('div', class_='menu-category')
                category = category_elem.get_text(strip=True) if category_elem else "Main Dish"
                print(f"Category: {category}")
                
                # Extract menu name
                name_elem = cell.find('div', class_='menu-name')
                name = name_elem.get_text(strip=True) if name_elem else ""
                print(f"Name: {name}")
                
                # Extract menu description
                desc_elems = cell.find_all('div', class_='menu-desc')
                descriptions = []
                for desc_elem in desc_elems:
                    desc_text = desc_elem.get_text(strip=True)
                    if desc_text:
                        descriptions.append(desc_text)
                print(f"Descriptions: {descriptions}")
                
                # Extract prices
                price_elems = cell.find_all('div', class_='menu-price')
                prices = []
                for price_elem in price_elems:
                    price_text = price_elem.get_text(strip=True)
                    if price_text:
                        prices.append(price_text)
                print(f"Prices: {prices}")
                
                # Process the item(s)
                if not name or len(name.strip()) < 2:
                    print("  → Skipping: no name")
                    continue
                
                # Determine if we have multiple prices for different sizes
                size_descriptions = [d for d in descriptions if d in ['klein', 'groß', 'small', 'large']]
                content_descriptions = [d for d in descriptions if d not in ['klein', 'groß', 'small', 'large']]
                
                # Combine name and content description
                full_description = name
                if content_descriptions:
                    full_description += f" - {' | '.join(content_descriptions)}"
                
                if len(prices) > 1 and len(size_descriptions) > 0:
                    # Multiple prices with sizes
                    for j, price in enumerate(prices):
                        size_desc = ""
                        if j < len(size_descriptions):
                            size_desc = f" ({size_descriptions[j]})"
                        
                        item_description = full_description + size_desc
                        menu_items.append({
                            'menu_date': today,
                            'category': category,
                            'description': item_description,
                            'price': price
                        })
                        print(f"  → Added: {item_description} - {price}")
                else:
                    # Single item
                    price = prices[0] if prices else None
                    menu_items.append({
                        'menu_date': today,
                        'category': category,
                        'description': full_description,
                        'price': price
                    })
                    print(f"  → Added: {full_description} - {price}")
                
            except Exception as e:
                print(f"  → Error processing cell {i+1}: {e}")
                continue
        
        print(f"\n=== Summary ===")
        print(f"Total menu items extracted: {len(menu_items)}")
        
        print(f"\n=== Menu Items ===")
        for item in menu_items:
            print(f"  {item['category']}: {item['description']} ({item['price']})")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_henry_scraper()