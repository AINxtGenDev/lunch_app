#!/usr/bin/env python3
"""
Manual scrape script for Albanco only
"""

from app.services.scraping_service import ScrapingService
from app import create_app

def main():
    app = create_app()
    
    with app.app_context():
        scraping_service = ScrapingService()
        
        # Run only Albanco scraper
        result = scraping_service.run_single_scraper("Albanco")
        
        print(f"Albanco scraper result: {result}")

if __name__ == "__main__":
    main()