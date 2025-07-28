#!/usr/bin/env python3
"""Analyze iki-restaurant.at website structure"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

def analyze_with_requests():
    """Try to fetch the page with requests first"""
    print("=== Analyzing with requests ===")
    url = "https://iki-restaurant.at/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save the HTML for inspection
        with open('iki_requests.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"HTML saved to iki_requests.html")
        
        # Look for PDF links
        pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
        print(f"\nFound {len(pdf_links)} PDF links:")
        for link in pdf_links:
            href = link.get('href')
            text = link.get_text(strip=True)
            print(f"  - {text}: {href}")
        
        # Look for menu-related text
        print("\nSearching for menu content...")
        
        # Look for text containing "tageskarte", "lunch", "menu"
        menu_keywords = ['tageskarte', 'lunch', 'menu', 'standardkarte']
        all_text = soup.get_text().lower()
        
        for keyword in menu_keywords:
            if keyword in all_text:
                print(f"Found '{keyword}' in page text")
                
                # Find links containing this keyword
                keyword_links = soup.find_all('a', string=lambda text: text and keyword in text.lower())
                for link in keyword_links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    print(f"  Link: {text} -> {href}")
            
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
        url = "https://iki-restaurant.at/"
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
        with open('iki_selenium.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"Rendered HTML saved to iki_selenium.html")
        
        # Look for PDF links
        pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
        print(f"\nFound {len(pdf_links)} PDF links:")
        for link in pdf_links:
            href = link.get_attribute("href")
            text = link.text.strip()
            print(f"  - {text}: {href}")
        
        # Look for menu-related links
        menu_keywords = ['tageskarte', 'lunch', 'menu', 'standardkarte']
        
        for keyword in menu_keywords:
            elements = driver.find_elements(By.XPATH, f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]")
            if elements:
                print(f"\nFound {len(elements)} links containing '{keyword}':")
                for elem in elements:
                    href = elem.get_attribute("href")
                    text = elem.text.strip()
                    print(f"  - {text}: {href}")
        
        # Print some sample text
        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = body_text.split('\n')
        print(f"\nFirst 30 lines of visible text:")
        for i, line in enumerate(lines[:30]):
            if line.strip():
                print(f"  {i}: {line.strip()}")
                
    except Exception as e:
        print(f"Error with Selenium: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

def check_pdf_url():
    """Check if the provided PDF URL is accessible"""
    print("\n=== Checking provided PDF URL ===")
    pdf_url = "https://iki-restaurant.at/wp-content/uploads/sites/2/2025/06/IKI_Standardkarte_LUNCH_DE_06.2025.pdf"
    
    try:
        response = requests.head(pdf_url)
        print(f"PDF URL status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ PDF is accessible")
            content_type = response.headers.get('content-type', '')
            content_length = response.headers.get('content-length', 'unknown')
            print(f"  Content-Type: {content_type}")
            print(f"  Content-Length: {content_length} bytes")
        else:
            print("✗ PDF not accessible")
            
    except Exception as e:
        print(f"Error checking PDF: {e}")

if __name__ == "__main__":
    analyze_with_requests()
    analyze_with_selenium()
    check_pdf_url()