# app.py
from datetime import date
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
# TODO: The import for MenuItem will fail if the model is not defined.
# from models.menu import db, MenuItem
from utils.scheduler import setup_scheduler
import config

app = Flask(__name__)
app.config.from_object(config)
socketio = SocketIO(app, cors_allowed_origins="*")
# db.init_app(app)

def get_today_menus():
    """
    Queries the database for today's menus and formats them.
    This is a placeholder implementation.
    """
    print("Fetching today's menus...")
    # In a real implementation, this would query the database.
    # today = date.today()
    # menu_items = MenuItem.query.filter_by(date=today).all()
    # ... formatting logic ...
    return []

def update_all_menus():
    """
    Triggers a manual update of all menus.
    This is a placeholder implementation.
    """
    print("Triggering manual menu update...")
    # This will eventually call the scraping logic.
    # For now, we can just emit the (empty) menu data back.
    menus = get_today_menus()
    socketio.emit('menu_update', menus)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect(auth=None):
    """
    Handles a new client connection.
    The 'auth' argument is sent by socketio but not used here.
    """
    # Send current menu data on connection
    menus = get_today_menus()
    emit('menu_update', menus)

@socketio.on('request_update')
def handle_update_request():
    # Trigger manual update
    update_all_menus()
    
if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    setup_scheduler(app, socketio)
    socketio.run(app, host='0.0.0.0', port=5000)