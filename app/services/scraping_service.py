# app/services/scraping_service.py
from flask import current_app
from datetime import date, timedelta
from sqlalchemy import func
from typing import List, Optional
import logging

from app import db, socketio
from app.models import Restaurant, MenuItem
from app.scrapers.erste_campus_scraper import ErsteCampusScraper
from app.scrapers.fouroh4_scraper import FourOh4Scraper
from app.scrapers.henry_scraper import HenryScraper
from app.scrapers.iki_scraper import IKIScraper
from app.scrapers.cafegeorge_scraper import CafeGeorgeScraper
from app.scrapers.campusbraeu_scraper import CampusBrauScraper
from app.scrapers.albanco_scraper import AlbancoScraper
from app.scrapers.cyclist_scraper import CyclistScraper


class ScrapingService:
    """
    Service class that manages all restaurant scrapers.
    Handles scheduling, execution, and database updates.
    """
    
    def __init__(self):
        """Initialize the scraping service with all configured scrapers."""
        self.logger = self._get_logger()
        
        # Initialize all scrapers
        self.scrapers = [
            ErsteCampusScraper(),
            FourOh4Scraper(),
            HenryScraper(),
            IKIScraper(),
            CafeGeorgeScraper(),
            CampusBrauScraper(),
            AlbancoScraper(),
            CyclistScraper(),
            # Add more scrapers here as they are developed:
            # KekkoSushiScraper(),
        ]
        
        self.logger.info(f"Initialized ScrapingService with {len(self.scrapers)} scrapers")
    
    def _get_logger(self) -> logging.Logger:
        """Get logger instance, handling both app context and standalone usage."""
        if current_app:
            return current_app.logger
        else:
            # Create standalone logger for testing
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
            if not logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                ))
                logger.addHandler(handler)
            return logger
    
    def run_all_scrapers(self) -> dict:
        """
        Run all configured scrapers and return statistics.
        
        Returns:
            dict: Statistics about the scraping run including successes, failures, and item counts
        """
        self.logger.info("=" * 60)
        self.logger.info("Starting scraping process for all restaurants")
        self.logger.info("=" * 60)
        
        stats = {
            'total_scrapers': len(self.scrapers),
            'successful': 0,
            'failed': 0,
            'total_items': 0,
            'errors': []
        }
        
        with current_app.app_context():
            for scraper in self.scrapers:
                try:
                    self.logger.info(f"\n▶ Running scraper for: {scraper.name}")
                    self.logger.info(f"  URL: {scraper.url}")
                    
                    # Run the scraper
                    menu_items = scraper.scrape()
                    
                    if menu_items:
                        # Save to database
                        scraper.save_to_db(menu_items)
                        
                        item_count = len(menu_items)
                        stats['successful'] += 1
                        stats['total_items'] += item_count
                        
                        self.logger.info(f"  ✅ Success: Saved {item_count} menu items")
                        
                        # Log sample items for verification
                        if menu_items and len(menu_items) > 0:
                            sample = menu_items[0]
                            self.logger.debug(
                                f"  Sample item: {sample.get('menu_date')} - "
                                f"{sample.get('category')} - {sample.get('description')[:50]}..."
                            )
                    else:
                        stats['failed'] += 1
                        stats['errors'].append({
                            'scraper': scraper.name,
                            'error': 'No data returned'
                        })
                        self.logger.warning(f"  ⚠️ Warning: No data returned from {scraper.name}")
                        
                except Exception as e:
                    stats['failed'] += 1
                    stats['errors'].append({
                        'scraper': scraper.name,
                        'error': str(e)
                    })
                    self.logger.error(
                        f"  ❌ Error: Failed to run scraper for {scraper.name}: {e}",
                        exc_info=True
                    )
            
            # Log summary
            self.logger.info("\n" + "=" * 60)
            self.logger.info("Scraping Summary:")
            self.logger.info(f"  Total scrapers: {stats['total_scrapers']}")
            self.logger.info(f"  Successful: {stats['successful']}")
            self.logger.info(f"  Failed: {stats['failed']}")
            self.logger.info(f"  Total items scraped: {stats['total_items']}")
            self.logger.info("=" * 60)
            
            # Notify connected clients
            if stats['successful'] > 0:
                self.notify_clients_of_update()
            
        return stats
    
    def run_single_scraper(self, restaurant_name: str) -> dict:
        """
        Run a single scraper by restaurant name.
        
        Args:
            restaurant_name: Name of the restaurant to scrape
            
        Returns:
            dict: Statistics about the scraping run
        """
        self.logger.info(f"Running single scraper for: {restaurant_name}")
        
        # Find the scraper
        scraper = None
        for s in self.scrapers:
            if s.name.lower() == restaurant_name.lower():
                scraper = s
                break
        
        if not scraper:
            self.logger.error(f"No scraper found for restaurant: {restaurant_name}")
            return {
                'success': False,
                'error': f'No scraper configured for {restaurant_name}'
            }
        
        # Run the scraper
        try:
            menu_items = scraper.scrape()
            if menu_items:
                scraper.save_to_db(menu_items)
                self.logger.info(f"Successfully scraped {len(menu_items)} items for {restaurant_name}")
                
                # Notify clients
                self.notify_clients_of_update()
                
                return {
                    'success': True,
                    'items_count': len(menu_items),
                    'restaurant': restaurant_name
                }
            else:
                return {
                    'success': False,
                    'error': 'No menu items found',
                    'restaurant': restaurant_name
                }
                
        except Exception as e:
            self.logger.error(f"Error scraping {restaurant_name}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'restaurant': restaurant_name
            }
    
    def notify_clients_of_update(self):
        """
        Notify all connected WebSocket clients about menu updates.
        Sends today's menu data to all connected clients.
        """
        try:
            self.logger.info("Notifying connected clients of menu update...")
            
            today = date.today()
            
            # Fetch updated menu data
            restaurants = Restaurant.query.all()
            menu_data = []
            
            for restaurant in restaurants:
                # Get today's menu items
                items = MenuItem.query.filter_by(
                    restaurant_id=restaurant.id,
                    menu_date=today
                ).order_by(MenuItem.category).all()
                
                # Format menu data
                menu_data.append({
                    "name": restaurant.name,
                    "last_updated": restaurant.last_scraped.isoformat() if restaurant.last_scraped else None,
                    "items": [
                        {
                            "category": item.category,
                            "description": item.description,
                            "price": item.price or ""
                        }
                        for item in items
                    ]
                })
            
            # Emit to all connected clients
            socketio.emit("menu_update", {
                "date": today.isoformat(),
                "data": menu_data,
                "timestamp": date.today().isoformat()
            })
            
            self.logger.info(
                f"Broadcast menu update for {len(menu_data)} restaurants "
                f"with {sum(len(r['items']) for r in menu_data)} total items"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to notify clients: {e}", exc_info=True)
    
    def get_scraper_status(self) -> List[dict]:
        """
        Get the status of all configured scrapers.
        
        Returns:
            List of scraper status dictionaries
        """
        status_list = []
        
        for scraper in self.scrapers:
            # Get last scrape info from database
            restaurant = Restaurant.query.filter_by(name=scraper.name).first()
            
            status = {
                'name': scraper.name,
                'url': scraper.url,
                'configured': True,
                'last_scraped': None,
                'items_count': 0
            }
            
            if restaurant:
                status['last_scraped'] = restaurant.last_scraped.isoformat() if restaurant.last_scraped else None
                
                # Count today's items
                today_count = MenuItem.query.filter_by(
                    restaurant_id=restaurant.id,
                    menu_date=date.today()
                ).count()
                
                status['items_count'] = today_count
            
            status_list.append(status)
        
        return status_list
    
    def cleanup_old_data(self, days_to_keep: int = 7):
        """
        Remove menu items older than specified days.
        
        Args:
            days_to_keep: Number of days of menu data to keep
        """
        try:
            cutoff_date = date.today() - timedelta(days=days_to_keep)
            
            # Delete old menu items
            deleted_count = MenuItem.query.filter(
                MenuItem.menu_date < cutoff_date
            ).delete()
            
            db.session.commit()
            
            self.logger.info(
                f"Cleaned up {deleted_count} menu items older than {cutoff_date}"
            )
            
            return deleted_count
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error cleaning up old data: {e}", exc_info=True)
            return 0
