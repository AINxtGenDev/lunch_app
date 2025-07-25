# run.py
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Use eventlet for production-ready async server
    # The host='0.0.0.0' makes it accessible from other devices on your network
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
