#!/bin/bash

echo "=== Checking Lunch App Status ==="
echo ""

echo "1. Service status:"
sudo systemctl status lunch-app --no-pager
echo ""

echo "2. Recent service logs:"
sudo journalctl -u lunch-app -n 30 --no-pager
echo ""

echo "3. Gunicorn logs (if they exist):"
if [ -f /home/stecher/lunch_app/logs/gunicorn_error.log ]; then
    echo "Error log:"
    tail -20 /home/stecher/lunch_app/logs/gunicorn_error.log
else
    echo "No gunicorn error log found"
fi
echo ""

if [ -f /home/stecher/lunch_app/logs/gunicorn_access.log ]; then
    echo "Access log:"
    tail -10 /home/stecher/lunch_app/logs/gunicorn_access.log
else
    echo "No gunicorn access log found"
fi
echo ""

echo "4. Database status:"
cd /home/stecher/lunch_app
if [ -f instance/app.db ]; then
    echo "Database file exists: $(ls -la instance/app.db)"
    /home/stecher/miniforge3/envs/lunch-menu-app/bin/python -c "
import sqlite3
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
tables = cursor.fetchall()
print('Tables:', [table[0] for table in tables])

cursor.execute('SELECT COUNT(*) FROM restaurant;')
restaurant_count = cursor.fetchone()[0]
print(f'Restaurants: {restaurant_count}')

cursor.execute('SELECT COUNT(*) FROM menu_item;')
menu_count = cursor.fetchone()[0]
print(f'Menu items: {menu_count}')

if menu_count > 0:
    cursor.execute('SELECT restaurant_id, COUNT(*) FROM menu_item GROUP BY restaurant_id;')
    items_per_restaurant = cursor.fetchall()
    print('Items per restaurant:', dict(items_per_restaurant))

conn.close()
"
else
    echo "Database file not found at instance/app.db"
fi
echo ""

echo "5. Testing direct access to app:"
curl -s -I http://localhost:7000 | head -5