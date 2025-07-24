# models/menu.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # soup, main, dessert, etc.
    item_name = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'restaurant': self.restaurant,
            'category': self.category,
            'item_name': self.item_name,
            'price': self.price,
            'date': self.date.isoformat()
        }