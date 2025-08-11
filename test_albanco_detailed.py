#!/usr/bin/env python3
"""Detailed debug script to see which dishes are found and which are missing"""

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
    
    print("=== CHECKING EACH DISH ===\n")
    
    # List of all 12 dishes that should be found
    all_dishes = [
        {'name': 'INSALATA AL BANCO', 'allergens': '(A,F,O)', 'price': '11,9', 'category': 'SALAD'},
        {'name': 'GNOCCHI PANCETTA E ZAFFERANO', 'allergens': '(A,C,G,O)', 'price': '14,9', 'category': 'PASTA'},
        {'name': 'RISOTTO ALLE MELANZANE', 'allergens': '(G,L,O)', 'price': '14,2', 'category': 'MAIN DISH'},
        {'name': 'CON GAMBERI', 'allergens': '(A,B,F,O)', 'price': '20,9', 'category': 'SALAD'},
        {'name': 'CON MOZZARELLA DI BUFALA', 'allergens': '(A,F,G,O)', 'price': '17,2', 'category': 'SALAD'},
        {'name': 'FILETTO DI SALMONE', 'allergens': '(D,G,O)', 'price': '19,5', 'category': 'MAIN DISH'},
        {'name': 'PASTA FREDDA ESTIVA', 'allergens': '(A,G,O)', 'price': '14,5', 'category': 'SALAD'},
        {'name': 'RAVIOLI CON VERDURE', 'allergens': '(A,C,G)', 'price': '14,2', 'category': 'PASTA'},
        {'name': 'INSALATA MISTA', 'allergens': '(O)', 'price': '5,9', 'category': 'SALAD'},
        {'name': 'SPAGHETTI ALL\'ARRABBIATA', 'allergens': '(A)', 'price': '14,2', 'category': 'PASTA'},
        {'name': 'SPAGHETTI AGLIO, OLIO E PEPERONCINO', 'allergens': '(A)', 'price': '13,2', 'category': 'PASTA'},
        {'name': 'TIRAMISÙ', 'allergens': '(A,C,G)', 'price': '6,2', 'category': 'DESSERT'},
    ]
    
    found_count = 0
    missing_dishes = []
    
    for dish in all_dishes:
        # Check if dish name exists in text
        dish_pattern = dish['name'].replace('\'', '[\'´]')
        
        if re.search(dish_pattern, text, re.IGNORECASE):
            print(f"✅ FOUND: {dish['name']} - {dish['price']}")
            found_count += 1
        else:
            print(f"❌ MISSING: {dish['name']} - {dish['price']}")
            missing_dishes.append(dish)
            
            # Check for partial matches
            words = dish['name'].split()
            for word in words:
                if len(word) > 3 and word in text:
                    print(f"   (Found word '{word}' in text)")
    
    print(f"\n=== SUMMARY ===")
    print(f"Found: {found_count}/12 dishes")
    
    if missing_dishes:
        print(f"\nMissing dishes:")
        for dish in missing_dishes:
            print(f"  - {dish['name']} ({dish['price']})")
    
    print("\n=== SCRAPER RESULTS ===")
    items = scraper.extract_menu_items()
    print(f"Scraper found {len(items)} items")
    
    # Check which dishes the scraper found
    scraper_found = []
    for item in items:
        # Extract dish name from description
        desc = item['description']
        for dish in all_dishes:
            if dish['name'] in desc or dish['name'].replace('\'', '´') in desc:
                scraper_found.append(dish['name'])
                break
    
    print(f"\nScraper found these dishes:")
    for name in scraper_found:
        print(f"  - {name}")