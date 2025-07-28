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
.
├── 00_readme.txt
├── analyze_erste_campus.py
├── analyze_iframe_content.py
├── api_page_props.json
├── api_response.json
├── app
│   ├── errors.py
│   ├── __init__.py
│   ├── models.py
│   ├── __pycache__
│   │   ├── errors.cpython-311.pyc
│   │   ├── __init__.cpython-311.pyc
│   │   ├── models.cpython-311.pyc
│   │   └── routes.cpython-311.pyc
│   ├── routes.py
│   ├── scrapers
│   │   ├── base_scraper.py
│   │   ├── erste_campus_scraper.py
│   │   └── __pycache__
│   │       ├── base_scraper.cpython-311.pyc
│   │       ├── erste_campus_api_scraper.cpython-311.pyc
│   │       ├── erste_campus_scraper.cpython-311.pyc
│   │       └── gourmet_api_scraper.cpython-311.pyc
│   ├── services
│   │   ├── __pycache__
│   │   │   └── scraping_service.cpython-311.pyc
│   │   └── scraping_service.py
│   ├── static
│   │   ├── css
│   │   │   └── style.css
│   │   └── js
│   │       └── main.js
│   └── templates
│       ├── base.html
│       ├── errors
│       │   ├── 404.html
│       │   ├── 500.html
│       │   └── error.html
│       └── index.html
├── app_minimal.py
├── CLAUDE.md
├── config.py
├── config_simple.py
├── debug_imports.py
├── diagnose_db_issue.py
├── download_api_data.py
├── environment.yaml
├── error.txt
├── erste_campus_advanced_scraper.py
├── erste_campus_final_scraper_fixed.py
├── erste_campus_final_scraper.py
├── erste_campus_iframe_content.html
├── erste_campus_iframe_pretty.html
├── erste_campus_iframe_scraper.py
├── erste_campus_nextjs_scraper.py
├── erste_campus_page.html
├── erste_campus_rendered.html
├── erste_campus_selenium_scraper.py
├── examine_menu_json.py
├── GEMINI.md
├── init_db.py
├── instance
│   ├── app.db
│   └── nonce_failure.png
├── LICENSE
├── logs
│   └── lunch_menu_app.log
├── menu_data.json
├── page_props.json
├── project-structure.txt
├── __pycache__
│   ├── config.cpython-311.pyc
│   └── examine_menu_json.cpython-311.pyc
├── react_data.json
├── README.md
├── run.py
├── selenium_rendered.html
├── setup_project.py
├── test_db.py
├── test_scraper.py
├── test_scraper_standalone.py
└── view_iframe_content.py
```

## Getting Started

conda env create -f environment.yaml
conda activate lunch-menu-app

## License
This project is licensed under the terms of the LICENSE file.
