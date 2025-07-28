#!/usr/bin/env python3
"""Test PDF extraction for IKI restaurant"""

import requests
import PyPDF2
import io
from datetime import datetime

def extract_pdf_text(pdf_url):
    """Extract text from PDF URL"""
    try:
        print(f"Downloading PDF from: {pdf_url}")
        response = requests.get(pdf_url)
        
        if response.status_code != 200:
            print(f"Failed to download PDF: {response.status_code}")
            return None
        
        # Create a PDF reader object
        pdf_file = io.BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        print(f"PDF has {len(pdf_reader.pages)} pages")
        
        # Extract text from all pages
        full_text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            full_text += f"\n=== Page {page_num + 1} ===\n"
            full_text += text
            print(f"Page {page_num + 1} extracted: {len(text)} characters")
        
        return full_text
        
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return None

def test_tageskarte():
    """Test extracting the main lunch menu"""
    print("=== Testing TAGESKARTE PDF ===")
    tageskarte_url = "https://iki-restaurant.at/wp-content/uploads/sites/2/2025/06/IKI_Standardkarte_LUNCH_DE_06.2025.pdf"
    
    text = extract_pdf_text(tageskarte_url)
    if text:
        # Save to file for analysis
        with open('iki_tageskarte.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Text saved to iki_tageskarte.txt")
        
        # Show first 1000 characters
        print("\nFirst 1000 characters of extracted text:")
        print(text[:1000])
        
        # Look for menu items
        lines = text.split('\n')
        print(f"\nTotal lines: {len(lines)}")
        
        # Look for price patterns
        price_lines = []
        for line in lines:
            if '€' in line or 'EUR' in line:
                price_lines.append(line.strip())
        
        print(f"\nFound {len(price_lines)} lines with prices:")
        for line in price_lines[:20]:  # Show first 20
            if line:
                print(f"  - {line}")

def test_lunch_specials():
    """Test extracting the weekly lunch specials"""
    print("\n=== Testing LUNCH SPECIALS PDF ===")
    specials_url = "https://iki-restaurant.at/wp-content/uploads/sites/2/2025/07/Lunch-KW-31.pdf"
    
    text = extract_pdf_text(specials_url)
    if text:
        # Save to file for analysis
        with open('iki_lunch_specials.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Text saved to iki_lunch_specials.txt")
        
        # Show first 1000 characters
        print("\nFirst 1000 characters of extracted text:")
        print(text[:1000])

if __name__ == "__main__":
    test_tageskarte()
    test_lunch_specials()