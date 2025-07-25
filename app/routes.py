# app/routes.py
from flask import Blueprint, render_template
from app import socketio
from .models import Restaurant, MenuItem
from sqlalchemy import func
from datetime import date

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """
    Serves the main page of the application.
    """
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """
    Handles a new client connection.
    Fetches the most recent menu data from the DB and sends it to the new client.
    """
    print('Client connected')
    
    # Find the most recent date for which we have menu items
    latest_date = db.session.query(func.max(MenuItem.menu_date)).scalar() or date.today()

    # Fetch all menu items for that most recent date
    restaurants = Restaurant.query.all()
    menu_data = []
    for restaurant in restaurants:
        items = MenuItem.query.filter_by(restaurant_id=restaurant.id, menu_date=latest_date).all()
        menu_data.append({
            'name': restaurant.name,
            'items': [{'category': item.category, 'description': item.description, 'price': item.price} for item in items]
        })
    
    # Emit the data to the newly connected client
    socketio.emit('initial_menu_load', {'data': menu_data})


@socketio.on('disconnect')
def handle_disconnect():
    """
    Handles a client disconnection.
    """
    print('Client disconnected')
