#!/bin/bash
# Daily scrape script for lunch menu app
# Add to crontab with: 0 5 * * * /home/nuc8/05_development/02_python/02_lunch_app/lunch_app/daily_scrape.sh

cd /home/nuc8/05_development/02_python/02_lunch_app/lunch_app
/home/nuc8/miniconda3/envs/lunch-menu-app/bin/python manual_scrape_today.py >> logs/daily_scrape.log 2>&1