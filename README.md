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
.
├── 00_readme.txt
├── GEMINI.md
├── LICENSE
├── README.md
├── docs
├── environment.yaml
├── init-project-script.sh
├── logs
├── models
│   └── __init__.py
├── project-structure.txt
├── quick_start.txt
├── scrapers
│   ├── __init__.py
│   └── base_scraper.py
├── scripts
├── static
│   ├── css
│   │   └── style.css
│   ├── images
│   └── js
│       └── app.js
├── templates
│   ├── base.html
│   └── index.html
├── tests
│   ├── __init__.py
│   └── conftest.py
└── utils
    ├── __init__.py
    ├── cache.py
    └── scheduler.py
```

## Getting Started

### Prerequisites
- Python 3.13+
- Conda for environment management
- A web browser

### Installation & Setup
1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd 02_lunch_app
    ```

2.  **Create and activate the Conda environment:**
    The `environment.yaml` file contains all the necessary dependencies.
    ```bash
    conda env create -f environment.yaml
    conda activate lunch-menu-app
    ```

3.  **Initialize the database (if required):**
    Run the initial setup script if one is provided in the `scripts` directory.

### Running the Application
1.  **Start the Flask application:**
    ```bash
    python app.py 
    ```
    *(Note: The main application file might have a different name, check the `scripts` for a run script)*

2.  **Open your browser:**
    Navigate to `http://127.0.0.1:5000` (or the configured address) to see the application.

## License
This project is licensed under the terms of the LICENSE file.
