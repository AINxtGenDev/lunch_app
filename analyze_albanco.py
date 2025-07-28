#!/usr/bin/env python3
"""Analyze albanco.at website structure"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime

def analyze_with_requests():
    """Try to fetch the page with requests first"""
    print("=== Analyzing with requests ===")
    url = "https://albanco.at/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save the HTML for inspection
        with open('albanco_requests.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"HTML saved to albanco_requests.html")
        
        # Look for menu-related links
        print("\nSearching for menu links...")
        
        # Look for links containing menu, weekly, menue
        menu_keywords = ['menu', 'menue', 'weekly', 'wochenkarte', 'speisekarte', 'kw', 'lunch']
        menu_links = soup.find_all('a', href=lambda x: x and any(keyword in x.lower() for keyword in menu_keywords))
        print(f"Found {len(menu_links)} links with menu keywords")
        for link in menu_links:
            print(f"  - {link.get_text(strip=True)}: {link.get('href')}")
        
        # Look for PDF links
        pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
        print(f"\nFound {len(pdf_links)} PDF links")
        for link in pdf_links:
            print(f"  - {link.get_text(strip=True)}: {link.get('href')}")
        
        # Look for current week pattern (KW31)
        current_week = datetime.now().isocalendar()[1]
        print(f"\nCurrent week: KW{current_week}")
        
        # Search for current week in text
        current_week_elements = soup.find_all(text=lambda text: text and f'kw{current_week}' in text.lower())
        print(f"Found {len(current_week_elements)} elements with current week")
        
        # Look for text containing menu-related words
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
        url = "https://albanco.at/"
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
        with open('albanco_selenium.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"Rendered HTML saved to albanco_selenium.html")
        
        # Look for weekly menu links
        print("\nLooking for weekly menu links...")
        
        # Find all links
        links = driver.find_elements(By.TAG_NAME, "a")
        menu_links = []
        for link in links:
            href = link.get_attribute("href") or ""
            text = link.text.strip()
            if any(keyword in href.lower() or keyword in text.lower() for keyword in ['menu', 'menue', 'weekly', 'wochenkarte', 'kw']):
                menu_links.append({'text': text, 'href': href})
                print(f"  - {text}: {href}")
        
        # Look for current week PDF pattern
        current_week = datetime.now().isocalendar()[1]
        print(f"\nLooking for current week KW{current_week} PDF...")
        
        # Try to find weekly menu link or button
        weekly_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'wöchentlich') or contains(text(), 'weekly') or contains(text(), 'Wochenkarte') or contains(text(), 'menue')]")
        print(f"Found {len(weekly_elements)} weekly-related elements")
        
        for elem in weekly_elements[:5]:  # Limit to first 5
            try:
                text = elem.text.strip()
                if text:
                    print(f"  - {text}")
            except:
                pass
        
        # Check for navigation or menu items
        nav_elements = driver.find_elements(By.TAG_NAME, "nav")
        if nav_elements:
            print(f"\nFound {len(nav_elements)} navigation elements")
            for i, nav in enumerate(nav_elements[:2]):  # First 2 navs
                try:
                    nav_text = nav.text.strip()
                    if nav_text:
                        print(f"  Nav {i+1}: {nav_text}")
                except:
                    pass
        
        # Look for buttons or clickable elements
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\nFound {len(buttons)} button elements")
        
        # Print page text for analysis (first 100 lines)
        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = body_text.split('\n')
        print(f"\nFirst 50 non-empty lines of page text:")
        count = 0
        for line in lines:
            if line.strip() and count < 50:
                print(f"  {count}: {line.strip()}")
                count += 1
                
    except Exception as e:
        print(f"Error with Selenium: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

def check_direct_pdf():
    """Check if we can access the PDF directly"""
    print("\n=== Checking Direct PDF Access ===")
    
    current_week = datetime.now().isocalendar()[1]
    pdf_url = f"https://albanco.at/wp-content/uploads/sites/3/2025/07/la4_KW{current_week}.pdf"
    
    print(f"Trying direct PDF access: {pdf_url}")
    
    try:
        response = requests.head(pdf_url)
        print(f"PDF Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Direct PDF access successful!")
            
            # Try to download and analyze
            pdf_response = requests.get(pdf_url)
            with open(f'albanco_KW{current_week}.pdf', 'wb') as f:
                f.write(pdf_response.content)
            print(f"PDF downloaded as albanco_KW{current_week}.pdf")
            
        else:
            print("❌ Direct PDF access failed")
            
    except Exception as e:
        print(f"Error accessing PDF: {e}")

if __name__ == "__main__":
    analyze_with_requests()
    analyze_with_selenium()
    check_direct_pdf()