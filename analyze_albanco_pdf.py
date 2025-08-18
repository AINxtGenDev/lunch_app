#!/usr/bin/env python3
"""Analyze the Albanco PDF to understand its structure."""

import requests
import pdfplumber
from io import BytesIO
import re

# Download the PDF
pdf_url = "https://albanco.at/wp-content/uploads/sites/3/2025/08/la4.pdf"
print(f"Downloading PDF from: {pdf_url}")
response = requests.get(pdf_url)
response.raise_for_status()

# Parse PDF
pdf_content = BytesIO(response.content)
with pdfplumber.open(pdf_content) as pdf:
    page = pdf.pages[0]
    text = page.extract_text()
    
    print("=" * 80)
    print("RAW PDF TEXT:")
    print("=" * 80)
    print(text)
    print("=" * 80)
    
    # Find all price patterns
    print("\nFOUND PRICES:")
    print("-" * 40)
    price_pattern = r'\d+[,\.]\d+'
    prices = re.findall(price_pattern, text)
    for i, price in enumerate(prices, 1):
        print(f"{i}. {price}")
    
    print(f"\nTotal prices found: {len(prices)}")
    
    # Find lines with prices
    print("\n" + "=" * 80)
    print("LINES CONTAINING PRICES:")
    print("=" * 80)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if re.search(r'\d+[,\.]\d+', line):
            print(f"Line {i}: {line}")
    
    # Try to extract dishes with pattern matching
    print("\n" + "=" * 80)
    print("ATTEMPTING TO EXTRACT DISHES:")
    print("=" * 80)
    
    # Pattern 1: DISH NAME (allergens) price
    pattern1 = r'([A-Z][A-ZÀÈÉÌÒÙ\s,\'\´]+?)\s*\(([A-Z,]+)\)\s*(\d+[,\.]\d+)'
    matches1 = re.findall(pattern1, text)
    print(f"\nPattern 1 (DISH (allergens) price): Found {len(matches1)} matches")
    for match in matches1:
        print(f"  - {match[0].strip()} ({match[1]}) - {match[2]}")
    
    # Pattern 2: Lines that look like dishes without allergens
    pattern2 = r'([A-Z]{2,}[A-ZÀÈÉÌÒÙ\s,\'\´]+?)\s+(\d+[,\.]\d+)'
    matches2 = re.findall(pattern2, text)
    print(f"\nPattern 2 (DISH price): Found {len(matches2)} matches")
    for match in matches2:
        if match[0].strip() not in ['KW', 'VEGANO', 'VEGETARIANO']:
            print(f"  - {match[0].strip()} - {match[1]}")