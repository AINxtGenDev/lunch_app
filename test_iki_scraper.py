#!/usr/bin/env python3
"""Test script for IKI scraper with detailed debugging"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.iki_scraper import IKIScraper
from datetime import datetime

def test_iki_scraper():
    """Test the IKI scraper with detailed output"""
    
    print("=== Testing IKI Scraper ===")
    
    scraper = IKIScraper()
    print(f"Scraper name: {scraper.name}")
    print(f"Scraper URL: {scraper.url}")
    
    print("\n=== Step 1: Finding current lunch PDF URL ===")
    pdf_url = scraper.find_current_lunch_pdf_url()
    if pdf_url:
        print(f"✓ Found PDF URL: {pdf_url}")
    else:
        print("✗ Could not find PDF URL")
        return
    
    print("\n=== Step 2: Extracting text from PDF ===")
    pdf_text = scraper.extract_text_from_pdf(pdf_url)
    if pdf_text:
        print(f"✓ Extracted {len(pdf_text)} characters")
        
        # Save text for inspection
        with open('iki_extracted_text.txt', 'w', encoding='utf-8') as f:
            f.write(pdf_text)
        print("✓ Text saved to iki_extracted_text.txt")
        
        # Show first 500 characters
        print(f"\nFirst 500 characters:")
        print(pdf_text[:500])
    else:
        print("✗ Could not extract text from PDF")
        return
    
    print("\n=== Step 3: Parsing menu items ===")
    menu_items = scraper.parse_menu_items_from_text(pdf_text)
    
    print(f"✓ Parsed {len(menu_items)} menu items")
    
    if menu_items:
        print("\n=== Menu Items ===")
        for i, item in enumerate(menu_items, 1):
            print(f"{i:2d}. {item['category']:<15} | {item['description']:<50} | {item['price']}")
    
    print("\n=== Step 4: Testing full scraper ===")
    try:
        all_items = scraper.scrape()
        print(f"✓ Full scraper returned {len(all_items)} items")
        
        if all_items != menu_items:
            print("⚠ Warning: Full scraper results differ from individual parsing")
    except Exception as e:
        print(f"✗ Full scraper failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_iki_scraper()