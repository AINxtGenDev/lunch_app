# app/scrapers/base_scraper.py
import logging
from abc import ABC, abstractmethod
from datetime import date, datetime

from app import db
from app.models import MenuItem, Restaurant

# Configure a dedicated logger for scrapers
logging.basicConfig(level=logging.INFO)
scraper_logger = logging.getLogger("scraper")


class BaseScraper(ABC):
    """
    Abstract base class for all restaurant menu scrapers.

    It enforces a common interface and provides helper methods for database
    interactions, ensuring consistency and reducing code duplication.
    """

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.logger = scraper_logger

    @abstractmethod
    def scrape(self):
        """
        The main method to perform scraping.
        This method must be implemented by each subclass.

        It should return a list of dictionaries, where each dictionary
        represents a menu item for a specific day.
        Example:
        [
            {
                'menu_date': date(2024, 7, 29),
                'category': 'Soup',
                'description': 'Tomato Soup',
                'price': '€ 4.50'
            },
            ...
        ]
        """
        pass

    def save_to_db(self, menu_items):
        """
        Saves the scraped menu items to the database.

        This method handles the database session, checks for existing data
        to prevent duplicates, and commits the changes.
        """
        if not menu_items:
            self.logger.info(f"No menu items found for {self.name}. Nothing to save.")
            return

        # Get or create the restaurant record
        restaurant = Restaurant.query.filter_by(name=self.name).first()
        if not restaurant:
            self.logger.info(f"Creating new restaurant entry for {self.name}")
            restaurant = Restaurant(name=self.name, url=self.url)
            db.session.add(restaurant)
            # Commit here to get the restaurant ID for the menu items
            db.session.commit()

        # Group items by date to perform checks more efficiently
        items_by_date = {}
        for item in menu_items:
            menu_date = item["menu_date"]
            if menu_date not in items_by_date:
                items_by_date[menu_date] = []
            items_by_date[menu_date].append(item)

        for menu_date, items in items_by_date.items():
            # Check if we already have menu items for this restaurant and date
            existing_item = MenuItem.query.filter_by(
                restaurant_id=restaurant.id, menu_date=menu_date
            ).first()

            if existing_item:
                self.logger.warning(
                    f"Menu for {self.name} on {menu_date} already exists. Deleting old entries to update."
                )
                # Delete all existing items for this day to ensure a fresh import
                MenuItem.query.filter_by(
                    restaurant_id=restaurant.id, menu_date=menu_date
                ).delete()
                db.session.commit()

            # Add the new items
            for item_data in items:
                new_item = MenuItem(
                    restaurant_id=restaurant.id,
                    menu_date=item_data["menu_date"],
                    category=item_data.get("category", "N/A"),
                    description=item_data.get("description", ""),
                    price=item_data.get("price", ""),
                )
                db.session.add(new_item)
            self.logger.info(
                f"Successfully added {len(items)} new menu items for {self.name} for {menu_date}."
            )

        restaurant.last_scraped = datetime.utcnow()
        db.session.commit()
        self.logger.info(f"Database update complete for {self.name}.")
