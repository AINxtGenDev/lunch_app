#!/usr/bin/env python
from app import create_app
from app.services.scraping_service import ScrapingService

app = create_app()
with app.app_context():
    print("Starting manual scrape for today's menus...")
    scraping_service = ScrapingService()
    results = scraping_service.run_all_scrapers()
    print("\nScraping completed!")
    print(f"Results: {results}")