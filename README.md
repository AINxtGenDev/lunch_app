# Raspberry Pi Lunch Menu Aggregator

## Project Overview
A Python-based web application that automatically scrapes daily lunch menus from multiple restaurant websites, including PDF-based weekly menus, and displays them in a modern, responsive interface. The application is designed to run on a Raspberry Pi.

## Features
- **Automated Scraping:** Scrapes daily menus from 5 different restaurant websites.
- **PDF Menu Support:** Includes a special handler for parsing weekly menus from PDF files.
- **Real-time Updates:** Uses Socket.IO to push menu updates to the web interface in real-time.
- **Modern UI:** A clean and responsive user interface built with HTML5, CSS3, and JavaScript.
- **Scheduled Tasks:** Automatically updates the menus every day at a scheduled time.
- **Caching:** Implements caching for better performance and to reduce redundant scraping.

## Technology Stack
- **Backend:** Python 3.13+, Flask
- **Real-time Updates:** Flask-SocketIO
- **Web Scraping:** BeautifulSoup4, Requests, Selenium (for dynamic content and PDFs)
- **Task Scheduling:** APScheduler
- **Database:** SQLite
- **Frontend:** HTML5, CSS3 (Grid/Flexbox), JavaScript
- **Environment Management:** Conda

## Project Structure
```
lunch-menu-app/
├── app/
│   ├── __init__.py         # Application factory (create_app)
│   ├── models.py           # SQLAlchemy database models
│   ├── routes.py           # Application routes and view logic
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base_scraper.py   # Abstract base class for all scrapers
│   │   ├── erste_campus_scraper.py
│   │   ├── four_oh_four_scraper.py
│   │   ├── henry_scraper.py
│   │   ├── kekko_sushi_scraper.py
│   │   └── iki_restaurant_scraper.py # For the PDF menu
│   ├── services/
│   │   ├── __init__.py
│   │   └── scraping_service.py # Manages scheduling and running scrapers
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Main stylesheet
│   │   └── js/
│   │       └── main.js       # Frontend JavaScript for Socket.IO
│   └── templates/
│       ├── base.html         # Base HTML template
│       └── index.html        # Main page
├── instance/
│   └── app.db              # SQLite database file (will be created here)
├── .env                    # Environment variables (SECRET_KEY, etc.) - VERY IMPORTANT
├── .gitignore              # Files to ignore in git
├── config.py               # Configuration settings (Dev, Prod)
├── environment.yaml        # Conda environment definition
└── run.py                  # Main entry point to run the application
```

## Getting Started

conda env create -f environment.yaml
conda activate lunch-menu-app

## License
This project is licensed under the terms of the LICENSE file.
