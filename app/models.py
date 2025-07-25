# app/models.py
from app import db
from datetime import datetime

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    url = db.Column(db.String(255), nullable=False)
    last_scraped = db.Column(db.DateTime, default=datetime.utcnow)
    menu_items = db.relationship('MenuItem', backref='restaurant', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Restaurant {self.name}>'

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    
    # The date the menu is for
    menu_date = db.Column(db.Date, nullable=False)
    
    # e.g., 'Soup', 'Main Dish 1', 'Vegetarian', 'Dessert'
    category = db.Column(db.String(100), nullable=False) 
    
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.String(20), nullable=True) # String to accommodate various formats (e.g., "€ 9,50", "CHF 12.-")

    # The date this record was scraped
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MenuItem {self.menu_date} - {self.category}: {self.description[:30]}>'
