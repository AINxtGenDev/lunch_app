#!/usr/bin/env python3
"""Find the current lunch specials PDF URL for IKI restaurant"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

def find_current_lunch_pdf():
    """Find the current lunch specials PDF URL"""
    try:
        print("=== Looking for current lunch PDF ===")
        url = "https://iki-restaurant.at/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all PDF links
        pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
        
        print(f"Found {len(pdf_links)} PDF links:")
        
        lunch_pdfs = []
        for link in pdf_links:
            href = link.get('href')
            text = link.get_text(strip=True).lower()
            
            print(f"  - {link.get_text(strip=True)}: {href}")
            
            # Look for lunch-related PDFs
            if any(keyword in text for keyword in ['lunch', 'special', 'kw', 'week']):
                lunch_pdfs.append({
                    'text': link.get_text(strip=True),
                    'url': href
                })
        
        print(f"\nFound {len(lunch_pdfs)} lunch-related PDFs:")
        for pdf in lunch_pdfs:
            print(f"  - {pdf['text']}: {pdf['url']}")
        
        # Try to determine which is the current week
        current_week = datetime.now().isocalendar()[1]
        current_year = datetime.now().year
        
        print(f"\nCurrent week: KW {current_week}, Year: {current_year}")
        
        # Look for current week in URL or text
        current_pdf = None
        for pdf in lunch_pdfs:
            url_text = pdf['url'].lower() + ' ' + pdf['text'].lower()
            
            # Check if URL contains current week
            if f'kw-{current_week}' in url_text or f'kw{current_week}' in url_text:
                current_pdf = pdf
                print(f"✓ Found current week PDF: {pdf['text']}")
                break
            
            # Check for patterns like "KW 31" in the filename
            week_match = re.search(r'kw[-\s]*(\d+)', url_text)
            if week_match:
                pdf_week = int(week_match.group(1))
                print(f"  PDF week: {pdf_week}")
                
                # Allow current week or next week (in case it's updated early)
                if pdf_week in [current_week, current_week + 1]:
                    current_pdf = pdf
                    print(f"✓ Found current/next week PDF: {pdf['text']}")
                    break
        
        if not current_pdf and lunch_pdfs:
            # Fallback: use the first lunch PDF found
            current_pdf = lunch_pdfs[0]
            print(f"⚠ Using fallback PDF: {current_pdf['text']}")
        
        return current_pdf['url'] if current_pdf else None
        
    except Exception as e:
        print(f"Error finding current lunch PDF: {e}")
        return None

if __name__ == "__main__":
    pdf_url = find_current_lunch_pdf()
    if pdf_url:
        print(f"\n✓ Current lunch PDF URL: {pdf_url}")
    else:
        print("\n✗ No current lunch PDF found")