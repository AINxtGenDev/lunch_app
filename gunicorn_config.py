import multiprocessing
import os

bind = "0.0.0.0:7000"
# Use only 1 worker to avoid SQLAlchemy threading issues
workers = 1
worker_class = "eventlet"
worker_connections = 1000
timeout = 120
keepalive = 2

accesslog = "/home/stecher/lunch_app/logs/gunicorn_access.log"
errorlog = "/home/stecher/lunch_app/logs/gunicorn_error.log"
loglevel = "info"

daemon = False
pidfile = "/home/stecher/lunch_app/gunicorn.pid"

# Disable preload_app to avoid SQLAlchemy threading issues
reload = False
preload_app = False

max_requests = 1000
max_requests_jitter = 50

capture_output = True
enable_stdio_inheritance = True

# Additional settings for Socket.IO and SQLAlchemy
worker_tmp_dir = "/dev/shm"
threads = 2