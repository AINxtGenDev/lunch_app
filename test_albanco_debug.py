#!/usr/bin/env python3
"""Debug script for Albanco scraper to see why items are missing"""

from app.scrapers.albanco_scraper import AlbancoScraper
import requests
import pdfplumber
from io import BytesIO
import re

# Create scraper
scraper = AlbancoScraper()

# Find PDF URL
pdf_url = scraper.find_current_weekly_pdf_url()
print(f"PDF URL: {pdf_url}\n")

# Download and extract text
response = requests.get(pdf_url, timeout=30)
pdf_content = BytesIO(response.content)

with pdfplumber.open(pdf_content) as pdf:
    page = pdf.pages[0]
    text = page.extract_text()
    
    print("=== RAW PDF TEXT ===")
    print(text)
    print("\n=== END OF RAW TEXT ===\n")
    
    # Look for all price patterns in the text
    print("=== ALL PRICES FOUND IN PDF ===")
    price_pattern = r'(\d+[,\.]\d+)'
    prices = re.findall(price_pattern, text)
    print(f"Found {len(prices)} prices: {prices}\n")
    
    # Look for dishes with prices (more aggressive pattern)
    print("=== ATTEMPTING TO FIND ALL DISHES ===")
    
    # Clean text for better parsing
    lines = text.split('\n')
    
    current_dish = []
    found_dishes = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line contains a price
        price_match = re.search(r'(\d+[,\.]\d+)\s*$', line)
        
        if price_match:
            # This line has a price - it might be a dish
            price = price_match.group(1)
            text_before_price = line[:price_match.start()].strip()
            
            # Check if there's text before the price
            if text_before_price:
                # Look for dish pattern (starts with caps, may have allergens)
                if re.match(r'^[A-Z]', text_before_price):
                    found_dishes.append({
                        'line': line,
                        'dish': text_before_price,
                        'price': price
                    })
        
        # Also check for dish names that might be on separate lines
        elif re.match(r'^[A-Z][A-Z\s]+\([A-Z,/]+\)', line):
            # This looks like a dish name with allergens
            current_dish = [line]
        elif current_dish and re.match(r'^\d+[,\.]\d+$', line):
            # This is just a price on its own line
            found_dishes.append({
                'line': ' '.join(current_dish) + ' ' + line,
                'dish': ' '.join(current_dish),
                'price': line
            })
            current_dish = []
    
    print(f"Found {len(found_dishes)} potential dishes:")
    for i, dish in enumerate(found_dishes, 1):
        print(f"{i}. {dish['dish'][:50]}... - {dish['price']}")
    
    print("\n=== SCRAPER RESULTS ===")
    items = scraper.extract_menu_items()
    print(f"Scraper found {len(items)} items:")
    for item in items:
        print(f"  {item['category']}: {item['description'][:50]}... - {item['price']}")