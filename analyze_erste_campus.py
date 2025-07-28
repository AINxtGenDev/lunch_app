# analyze_erste_campus.py
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re

def analyze_with_requests():
    """First, try with requests to see what we get."""
    print("\n📋 Analyzing with requests library...")
    print("=" * 60)
    
    url = "https://erstecampus.at/en/kantine-am-campus-menu/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for common menu-related elements
        print("\n🔍 Looking for menu-related content...")
        
        # Check for iframes
        iframes = soup.find_all('iframe')
        if iframes:
            print(f"\n📌 Found {len(iframes)} iframe(s):")
            for i, iframe in enumerate(iframes, 1):
                print(f"  {i}. src: {iframe.get('src', 'No src')}")
                print(f"     id: {iframe.get('id', 'No id')}")
        
        # Look for divs with menu-related classes
        menu_keywords = ['menu', 'speise', 'food', 'dish', 'meal', 'kantine', 'gourmet']
        for keyword in menu_keywords:
            elements = soup.find_all(['div', 'section'], class_=re.compile(keyword, re.I))
            if elements:
                print(f"\n📌 Found {len(elements)} elements with '{keyword}' in class")
        
        # Check for JavaScript that might load content
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and any(keyword in script.string.lower() for keyword in ['menu', 'gourmet', 'api']):
                print(f"\n📌 Found relevant JavaScript:")
                print(script.string[:200] + "..." if len(script.string) > 200 else script.string)
                
        # Save the HTML for manual inspection
        with open('erste_campus_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("\n💾 Saved HTML to 'erste_campus_page.html' for inspection")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def analyze_with_selenium():
    """Use Selenium to handle JavaScript-rendered content."""
    print("\n\n🌐 Analyzing with Selenium (JavaScript rendering)...")
    print("=" * 60)
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    
    driver = None
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        url = "https://erstecampus.at/en/kantine-am-campus-menu/"
        print(f"🔗 Loading: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Check for iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            print(f"\n📌 Found {len(iframes)} iframe(s)")
            for i, iframe in enumerate(iframes):
                src = iframe.get_attribute('src')
                print(f"  {i+1}. src: {src}")
                
                # If it's a Gourmet iframe, switch to it
                if src and 'gourmet' in src.lower():
                    print(f"\n🎯 Found Gourmet iframe! Switching to it...")
                    driver.switch_to.frame(iframe)
                    
                    # Wait for content to load in iframe
                    time.sleep(3)
                    
                    # Get iframe content
                    iframe_html = driver.page_source
                    iframe_soup = BeautifulSoup(iframe_html, 'html.parser')
                    
                    # Look for menu items in iframe
                    menu_items = iframe_soup.find_all(['div', 'li', 'article'], 
                                                     class_=re.compile('menu|meal|dish|food', re.I))
                    print(f"  Found {len(menu_items)} potential menu items in iframe")
                    
                    # Save iframe content
                    with open('erste_campus_iframe.html', 'w', encoding='utf-8') as f:
                        f.write(iframe_html)
                    print("  💾 Saved iframe HTML to 'erste_campus_iframe.html'")
                    
                    # Switch back to main content
                    driver.switch_to.default_content()
        
        # Check for dynamically loaded content
        print("\n🔍 Checking for dynamically loaded content...")
        
        # Try to find menu containers
        menu_selectors = [
            "div[class*='menu']",
            "div[class*='meal']",
            "div[class*='speise']",
            "div[class*='gourmet']",
            ".menu-container",
            "#menu",
            "[data-menu]"
        ]
        
        for selector in menu_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"  ✅ Found {len(elements)} elements matching '{selector}'")
        
        # Save the fully rendered page
        with open('erste_campus_rendered.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("\n💾 Saved rendered HTML to 'erste_campus_rendered.html'")
        
        # Check browser console for errors
        logs = driver.get_log('browser')
        if logs:
            print("\n📋 Browser console messages:")
            for log in logs[:5]:  # Show first 5 logs
                print(f"  {log['level']}: {log['message']}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

def check_gourmet_widget():
    """Check if there's a Gourmet widget embedded."""
    print("\n\n🍽️ Checking for Gourmet widget...")
    print("=" * 60)
    
    # Common Gourmet widget URLs
    gourmet_urls = [
        "https://www.gourmet.at/widget/",
        "https://widget.gourmet.at/",
        "https://www.gourmet-group.com/widget/"
    ]
    
    for url in gourmet_urls:
        try:
            response = requests.head(url, timeout=5)
            print(f"  {url}: {response.status_code}")
        except:
            print(f"  {url}: Failed to connect")

if __name__ == "__main__":
    print("🔍 Erste Campus Menu Analysis")
    print("=" * 60)
    
    # Run all analysis methods
    analyze_with_requests()
    analyze_with_selenium()
    check_gourmet_widget()
    
    print("\n\n✅ Analysis complete! Check the saved HTML files for details.")
