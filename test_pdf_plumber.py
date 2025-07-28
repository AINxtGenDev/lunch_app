#!/usr/bin/env python3
"""Test PDF extraction with pdfplumber for IKI restaurant"""

import requests
import pdfplumber
import io
from datetime import datetime

def extract_pdf_with_plumber(pdf_url):
    """Extract text from PDF URL using pdfplumber"""
    try:
        print(f"Downloading PDF from: {pdf_url}")
        response = requests.get(pdf_url)
        
        if response.status_code != 200:
            print(f"Failed to download PDF: {response.status_code}")
            return None
        
        # Create a PDF file object
        pdf_file = io.BytesIO(response.content)
        
        full_text = ""
        with pdfplumber.open(pdf_file) as pdf:
            print(f"PDF has {len(pdf.pages)} pages")
            
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    full_text += f"\n=== Page {page_num + 1} ===\n"
                    full_text += text
                    print(f"Page {page_num + 1} extracted: {len(text)} characters")
                else:
                    print(f"Page {page_num + 1}: No text extracted")
        
        return full_text
        
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_tageskarte_plumber():
    """Test extracting the main lunch menu with pdfplumber"""
    print("=== Testing TAGESKARTE PDF with pdfplumber ===")
    tageskarte_url = "https://iki-restaurant.at/wp-content/uploads/sites/2/2025/06/IKI_Standardkarte_LUNCH_DE_06.2025.pdf"
    
    text = extract_pdf_with_plumber(tageskarte_url)
    if text:
        # Save to file for analysis
        with open('iki_tageskarte_plumber.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Text saved to iki_tageskarte_plumber.txt")
        
        # Show first 2000 characters
        print("\nFirst 2000 characters of extracted text:")
        print(text[:2000])
        
        # Look for menu items
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        print(f"\nTotal non-empty lines: {len(lines)}")
        
        # Look for price patterns
        price_lines = []
        for line in lines:
            if '€' in line or 'EUR' in line:
                price_lines.append(line)
        
        print(f"\nFound {len(price_lines)} lines with prices:")
        for line in price_lines[:20]:  # Show first 20
            if line:
                print(f"  - {line}")

if __name__ == "__main__":
    test_tageskarte_plumber()