#!/usr/bin/env python3
"""
Manual scrape script for Campus Bräu only
"""

from app.services.scraping_service import ScrapingService
from app import create_app

def main():
    app = create_app()
    
    with app.app_context():
        scraping_service = ScrapingService()
        
        # Run only Campus Bräu scraper
        result = scraping_service.run_single_scraper("Campus Bräu")
        
        print(f"Campus Bräu scraper result: {result}")

if __name__ == "__main__":
    main()