#!/usr/bin/env python
from app import create_app, db
from app.models import MenuItem, Restaurant
from datetime import date, timedelta

app = create_app()
with app.app_context():
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Check menu items
    items_today = MenuItem.query.filter_by(menu_date=today).all()
    items_yesterday = MenuItem.query.filter_by(menu_date=yesterday).all()
    
    print(f"Menu items for today ({today}): {len(items_today)}")
    print(f"Menu items for yesterday ({yesterday}): {len(items_yesterday)}")
    
    # Check restaurants
    restaurants = Restaurant.query.all()
    print(f"\nTotal restaurants: {len(restaurants)}")
    for r in restaurants:
        print(f"  - {r.name}: last scraped {r.last_scraped}")
    
    # Check if scheduler ran today
    print(f"\nChecking if any scraping happened today...")
    from datetime import datetime
    today_start = datetime.combine(today, datetime.min.time())
    recent_items = MenuItem.query.filter(MenuItem.scraped_at >= today_start).all()
    print(f"Items scraped today: {len(recent_items)}")