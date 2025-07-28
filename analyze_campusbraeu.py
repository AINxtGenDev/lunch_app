#!/usr/bin/env python3
"""Analyze campusbraeu.at website structure"""

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
    url = "https://www.campusbraeu.at/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save the HTML for inspection
        with open('campusbraeu_requests.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"HTML saved to campusbraeu_requests.html")
        
        # Look for menu-related links
        print("\nSearching for menu links...")
        
        # Look for links containing speisekarte
        speisekarte_links = soup.find_all('a', href=lambda x: x and 'speisekarte' in x.lower())
        print(f"Found {len(speisekarte_links)} links with 'speisekarte'")
        for link in speisekarte_links:
            print(f"  - {link.get_text(strip=True)}: {link.get('href')}")
        
        # Look for menu-related text
        menu_keywords = ['speisekarte', 'menu', 'menü', 'lunch', 'mittagsmenü', 'tagesmenü']
        for keyword in menu_keywords:
            elements = soup.find_all(text=lambda text: text and keyword.lower() in text.lower())
            if elements:
                print(f"Found {len(elements)} elements containing '{keyword}'")
                
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
        url = "https://www.campusbraeu.at/"
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
        with open('campusbraeu_selenium.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"Rendered HTML saved to campusbraeu_selenium.html")
        
        # Look for menu links
        print("\nLooking for menu/speisekarte links...")
        
        # Find all links
        links = driver.find_elements(By.TAG_NAME, "a")
        menu_links = []
        for link in links:
            href = link.get_attribute("href") or ""
            text = link.text.strip()
            if any(keyword in href.lower() or keyword in text.lower() for keyword in ['speisekarte', 'menu', 'menü']):
                menu_links.append({'text': text, 'href': href})
                print(f"  - {text}: {href}")
        
        # Click on SPEISEKARTE link if found
        if menu_links:
            print("\nTrying to navigate to SPEISEKARTE...")
            for link_info in menu_links:
                if 'speisekarte' in link_info['text'].lower():
                    try:
                        # Find and click the link
                        link_elem = driver.find_element(By.LINK_TEXT, link_info['text'])
                        link_elem.click()
                        
                        # Wait for new page to load
                        time.sleep(3)
                        
                        # Get new page content
                        new_page_source = driver.page_source
                        new_soup = BeautifulSoup(new_page_source, 'html.parser')
                        
                        # Save speisekarte page
                        with open('campusbraeu_speisekarte.html', 'w', encoding='utf-8') as f:
                            f.write(new_soup.prettify())
                        
                        print(f"Saved speisekarte page to campusbraeu_speisekarte.html")
                        
                        # Analyze speisekarte page
                        print("\nAnalyzing speisekarte page...")
                        
                        # Look for price patterns
                        price_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
                        print(f"Found {len(price_elements)} elements with prices")
                        
                        # Print sample text
                        body_text = driver.find_element(By.TAG_NAME, "body").text
                        lines = body_text.split('\n')
                        print(f"\nFirst 50 non-empty lines:")
                        count = 0
                        for line in lines:
                            if line.strip() and count < 50:
                                print(f"  {count}: {line.strip()}")
                                count += 1
                        
                        break
                        
                    except Exception as e:
                        print(f"Error clicking link: {e}")
                
    except Exception as e:
        print(f"Error with Selenium: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    analyze_with_requests()
    analyze_with_selenium()