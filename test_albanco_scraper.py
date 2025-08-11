#!/usr/bin/env python3
"""Test script for Albanco scraper with detailed debugging"""
 
from app.scrapers.albanco_scraper import AlbancoScraper
import logging

# Set up logging to see debug output
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')

# Create scraper and test
scraper = AlbancoScraper()
items = scraper.extract_menu_items()

print(f'\n=== FOUND {len(items)} MENU ITEMS ===')
for item in items:
    print(f"{item['category']}: {item['description'][:60]}... - {item['price']}")
