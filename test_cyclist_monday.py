#!/usr/bin/env python3
"""
Test script to verify Cyclist scraper for Monday, September 1, 2025
Expected menu items:
- MINUTE STEAK Pepper sauce  
- RATATOUILLE Polenta
"""

import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
import re
from PIL import Image
import pytesseract
import io

def test_flipsnack_url():
    """Test direct access to the Flipsnack URL and extract menu content."""
    
    url = "https://www.flipsnack.com/EE9BE6CC5A8/wochenmen-14-20-08-2023/full-view.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'no-cache'
    }
    
    print(f"📅 Today is: {date.today().strftime('%A, %B %d, %Y')}")
    print(f"🔗 Testing URL: {url}")
    print("-" * 80)
    
    try:
        # Fetch the page
        response = requests.get(url, headers=headers, timeout=30)
        print(f"✅ Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for the flipbook viewer iframe or embed
            print("\n🔍 Looking for flipbook content...")
            
            # Strategy 1: Find iframe with flipbook content
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src', '')
                print(f"  Found iframe: {src[:100]}...")
            
            # Strategy 2: Look for Open Graph image (often contains menu preview)
            og_image = None
            for meta in soup.find_all('meta'):
                if meta.get('property') == 'og:image':
                    og_image = meta.get('content')
                    print(f"\n📸 Found Open Graph image: {og_image}")
                    break
            
            # Strategy 3: Look for direct image links in the page
            print("\n🖼️ Looking for menu images...")
            img_urls = []
            
            # Check for image URLs in scripts
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Look for image URLs in JavaScript
                    img_matches = re.findall(r'"(https://[^"]*\.(?:jpg|jpeg|png)[^"]*)"', script.string)
                    img_urls.extend(img_matches)
            
            # Also check img tags
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src and ('menu' in src.lower() or 'woche' in src.lower() or 'tage' in src.lower()):
                    img_urls.append(src)
            
            if img_urls:
                print(f"  Found {len(img_urls)} potential menu images")
                for i, img_url in enumerate(img_urls[:3]):  # Show first 3
                    print(f"  {i+1}. {img_url[:100]}...")
            
            # Try to extract text content
            print("\n📝 Extracting text content...")
            
            # Get all text from the page
            text_content = soup.get_text()
            
            # Look for Monday menu items
            lines = text_content.split('\n')
            monday_found = False
            menu_items = []
            
            for i, line in enumerate(lines):
                line_clean = line.strip()
                if not line_clean:
                    continue
                    
                # Check for Monday
                if 'MONTAG' in line_clean.upper() or 'MONDAY' in line_clean.upper():
                    monday_found = True
                    print(f"\n🗓️ Found Monday section at line {i}: {line_clean}")
                    
                    # Look at next 10 lines for menu items
                    for j in range(i+1, min(i+11, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and len(next_line) > 5:
                            # Check if it's a day name (stop if we hit another day)
                            if any(day in next_line.upper() for day in ['DIENSTAG', 'MITTWOCH', 'DONNERSTAG', 'FREITAG', 'TUESDAY', 'WEDNESDAY']):
                                break
                            # Skip obvious non-menu items
                            if not any(skip in next_line.upper() for skip in ['CYCLIST', 'TAGESTELLER', '©', 'COPYRIGHT']):
                                menu_items.append(next_line)
                                print(f"    → {next_line}")
            
            # Try OCR on Open Graph image if available
            if og_image and not menu_items:
                print(f"\n🔬 Attempting OCR on Open Graph image...")
                try:
                    img_response = requests.get(og_image, headers=headers, timeout=15)
                    if img_response.status_code == 200:
                        image = Image.open(io.BytesIO(img_response.content))
                        
                        # Convert to RGB if necessary
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        # OCR the image
                        ocr_text = pytesseract.image_to_string(image, lang='deu+eng')
                        
                        print("📄 OCR Text (first 500 chars):")
                        print(ocr_text[:500])
                        
                        # Look for Monday menu items in OCR text
                        ocr_lines = ocr_text.split('\n')
                        monday_section = False
                        
                        for line in ocr_lines:
                            line_upper = line.upper().strip()
                            
                            if 'MONTAG' in line_upper:
                                monday_section = True
                                print(f"\n✅ Found MONTAG in OCR text")
                            elif monday_section and any(day in line_upper for day in ['DIENSTAG', 'MITTWOCH', 'DONNERSTAG']):
                                monday_section = False
                            elif monday_section and len(line.strip()) > 10:
                                print(f"  Monday item: {line.strip()}")
                                
                except Exception as e:
                    print(f"❌ OCR failed: {e}")
            
            # Check for expected menu items
            print("\n🎯 Checking for expected menu items:")
            print("  Looking for: MINUTE STEAK Pepper sauce")
            print("  Looking for: RATATOUILLE Polenta")
            
            full_text = str(soup).upper()
            if 'MINUTE STEAK' in full_text or 'STEAK' in full_text:
                print("  ✅ Found STEAK reference")
            if 'RATATOUILLE' in full_text:
                print("  ✅ Found RATATOUILLE reference")
            if 'POLENTA' in full_text:
                print("  ✅ Found POLENTA reference")
            
        else:
            print(f"❌ Failed to fetch page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_flipsnack_url()