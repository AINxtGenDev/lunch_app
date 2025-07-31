#!/bin/bash

echo "=== Debugging Lunch App Service ==="
echo ""

echo "1. Checking if gunicorn is installed in conda environment:"
/home/stecher/miniconda3/envs/lunch-menu-app/bin/python -c "import gunicorn; print('Gunicorn version:', gunicorn.__version__)"
echo ""

echo "2. Checking if eventlet is installed:"
/home/stecher/miniconda3/envs/lunch-menu-app/bin/python -c "import eventlet; print('Eventlet installed successfully')"
echo ""

echo "3. Testing gunicorn directly:"
cd /home/stecher/lunch_app
/home/stecher/miniconda3/envs/lunch-menu-app/bin/gunicorn --version
echo ""

echo "4. Checking if app can be imported:"
cd /home/stecher/lunch_app
/home/stecher/miniconda3/envs/lunch-menu-app/bin/python -c "from run import app; print('App imported successfully')"
echo ""

echo "5. Trying to run gunicorn manually:"
cd /home/stecher/lunch_app
/home/stecher/miniconda3/envs/lunch-menu-app/bin/gunicorn --bind 0.0.0.0:7000 --workers 1 run:app