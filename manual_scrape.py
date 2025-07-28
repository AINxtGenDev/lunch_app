#!/usr/bin/env python3
"""Manual scraping trigger for testing"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.scraping_service import ScrapingService
from app import create_app

app = create_app()

with app.app_context():
    print("Starting manual scrape...")
    scraping_service = ScrapingService()
    scraping_service.run_all_scrapers()
    print("Scraping complete!")