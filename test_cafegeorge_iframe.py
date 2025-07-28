#!/usr/bin/env python3
"""Test Café George iframe content"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def test_cafegeorge_iframe():
    """Test the Café George iframe content"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Load the iframe URL directly
        iframe_url = "https://erstecampus.at/mealplan/2025/external/single/george-en.html"
        print(f"Loading iframe URL: {iframe_url}")
        
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
        with open('cafegeorge_iframe_content.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("Saved iframe content to cafegeorge_iframe_content.html")
        
        # Analyze the structure
        print("\n=== Page Structure Analysis ===")
        
        # Look for meal cards (same structure as 4oh4)
        meal_cards = soup.find_all('div', class_='meal-card')
        print(f"Found {len(meal_cards)} meal cards")
        
        if meal_cards:
            print("\n=== Sample Menu Items ===")
            for i, card in enumerate(meal_cards[:5]):  # Show first 5
                # Extract title
                title_elem = card.find('div', class_='meal-card-title')
                title = title_elem.get_text(strip=True) if title_elem else "Unknown"
                
                # Extract price
                price_elem = card.find('div', class_='meal-card-price')
                price = "N/A"
                if price_elem:
                    price_span = price_elem.find('span')
                    if price_span:
                        price = price_span.get_text(strip=True)
                
                # Extract category
                category = "Main Dish"
                category_elem = card.find('div', class_='meal-card-header')
                if category_elem:
                    category = category_elem.get_text(strip=True)
                
                print(f"{i+1}. {category}: {title} - {price}")
        
        # Check for day tabs
        day_tabs = soup.find_all('button', class_='day-tab')
        print(f"\nFound {len(day_tabs)} day tabs")
        for tab in day_tabs:
            day = tab.find('span', class_='day-tab__day')
            date = tab.find('span', class_='day-tab__date')
            if day and date:
                print(f"  - {day.get_text(strip=True)}: {date.get_text(strip=True)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_cafegeorge_iframe()