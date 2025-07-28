# app/routes.py
from flask import Blueprint, render_template, jsonify, request
from sqlalchemy import func
from datetime import date, datetime

from app import db, socketio
from .models import Restaurant, MenuItem

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """
    Serves the main page of the application.
    """
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    return render_template("index.html", current_date=current_date)


@main.route("/api/menus")
def get_menus():
    """
    API endpoint to get menu data with optional date filtering.
    """
    # Input validation for date parameter
    date_str = request.args.get('date')
    if date_str:
        try:
            menu_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    else:
        menu_date = date.today()
    
    restaurants = Restaurant.query.all()
    menu_data = []
    
    for restaurant in restaurants:
        items = MenuItem.query.filter_by(
            restaurant_id=restaurant.id, 
            menu_date=menu_date
        ).all()
        
        menu_data.append({
            "id": restaurant.id,
            "name": restaurant.name,
            "url": restaurant.url,
            "last_scraped": restaurant.last_scraped.isoformat() if restaurant.last_scraped else None,
            "items": [
                {
                    "category": item.category,
                    "description": item.description,
                    "price": item.price if item.price else ""
                }
                for item in items
            ]
        })
    
    return jsonify({
        "date": menu_date.isoformat(),
        "restaurants": menu_data
    })


@socketio.on("connect")
def handle_connect(auth=None):
    """
    Handles a new client connection with authentication support.
    """
    print(f"Client connected from {request.remote_addr}")
    
    today = date.today()
    restaurants = Restaurant.query.all()
    menu_data = []
    
    for restaurant in restaurants:
        items = MenuItem.query.filter_by(
            restaurant_id=restaurant.id, 
            menu_date=today
        ).all()
        
        menu_data.append({
            "name": restaurant.name,
            "items": [
                {
                    "category": item.category,
                    "description": item.description,
                    "price": item.price
                }
                for item in items
            ]
        })
    
    # Emit data to the newly connected client
    socketio.emit("initial_menu_load", {"data": menu_data}, room=request.sid)


@socketio.on("disconnect")
def handle_disconnect():
    """
    Handles a client disconnection.
    """
    print(f"Client disconnected from {request.remote_addr}")


@socketio.on("request_refresh")
def handle_refresh_request():
    """
    Handles manual refresh requests from clients.
    """
    socketio.emit("refresh_status", {"status": "processing"}, room=request.sid)
    
    # Trigger a scrape in the background
    from .services.scraping_service import ScrapingService
    scraping_service = ScrapingService()
    
    # Run in background to avoid blocking
    socketio.start_background_task(scraping_service.run_all_scrapers)
    
    return {"status": "accepted"}
