# Lunch Menu Aggregator

## Project Overview
A Python-based web application that automatically scrapes daily lunch menus from multiple restaurant websites and displays them in a modern, responsive interface. The application features real-time updates and supports various menu formats including HTML tables, iframes, and PDF documents.

## Features
- **Automated Scraping:** Scrapes daily menus from 7 different restaurant websites
- **Multi-Format Support:** Handles HTML tables, iframes, PDF documents, and dynamic JavaScript content
- **Real-time Updates:** Uses Socket.IO to push menu updates to the web interface in real-time
- **Modern UI:** Clean and responsive user interface built with HTML5, CSS3, and JavaScript
- **Scheduled Tasks:** Automatically updates menus daily at 5:00 AM using APScheduler
- **Database Storage:** Persistent menu storage with SQLite database
- **Rate Limiting:** Built-in rate limiting for API protection
- **Error Handling:** Comprehensive error handling and logging

## Supported Restaurants & URLs

| Restaurant | URL | Format | Items |
|------------|-----|--------|-------|
| **Erste Campus** | https://erstecampus.at/mealplan/ | iframe | 9 items |
| **4oh4** | https://4oh4.at/lunch-menu/ | iframe | 11 items |
| **Enjoy Henry** | https://www.enjoyhenry.com/menuplan-bdo/ | HTML table | 9 items |
| **IKI Restaurant** | https://iki-restaurant.at/ | PDF (weekly) | 5 items |
| **Cafe George** | https://cafegeorge.at/en/weekly-menu-en/ | iframe | 13 items |
| **Campus Bräu** | https://www.campusbraeu.at/ | HTML (weekly) | 3 items |
| **Albanco** | https://albanco.at/ | PDF (weekly) | 5 items |

## Technology Stack

### Backend
- **Python 3.11+** with Conda environment management
- **Flask** web framework with extensions:
  - Flask-SocketIO (real-time WebSocket communication)
  - Flask-SQLAlchemy (database ORM)
  - Flask-Limiter (rate limiting)
- **Web Scraping:**
  - BeautifulSoup4 (HTML parsing)
  - Selenium WebDriver (dynamic content)
  - PyPDF2 & pdfplumber (PDF text extraction)
  - Requests (HTTP requests)
- **Database:** SQLite with SQLAlchemy ORM
- **Scheduling:** APScheduler for cron-like scheduling
- **Logging:** Python logging with file rotation

### Frontend
- **HTML5** with semantic markup
- **CSS3** with Grid/Flexbox layout
- **Vanilla JavaScript** with Socket.IO client
- **Real-time Updates** via WebSocket

### Development Tools
- **Chrome WebDriver Manager** for automated browser management
- **Conda** for environment and dependency management

## Project Structure
```
lunch_app/
├── app/                           # Main application package
│   ├── __init__.py               # Flask app factory
│   ├── models.py                 # Database models (Restaurant, MenuItem)
│   ├── routes.py                 # HTTP route handlers
│   ├── errors.py                 # Error handlers
│   ├── scrapers/                 # Scraper implementations
│   │   ├── base_scraper.py       # Abstract base scraper class
│   │   ├── erste_campus_scraper.py  # Erste Campus scraper
│   │   ├── fouroh4_scraper.py       # 4oh4 restaurant scraper
│   │   ├── henry_scraper.py         # Enjoy Henry scraper
│   │   ├── iki_scraper.py           # IKI Restaurant PDF scraper
│   │   ├── cafegeorge_scraper.py    # Cafe George scraper
│   │   ├── campusbraeu_scraper.py   # Campus Bräu scraper
│   │   └── albanco_scraper.py       # Albanco PDF scraper
│   ├── services/
│   │   └── scraping_service.py   # Orchestrates all scrapers
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css         # Application styles
│   │   ├── js/
│   │   │   └── main.js           # Frontend JavaScript
│   │   └── image/                # Static images
│   └── templates/
│       ├── base.html             # Base template
│       ├── index.html            # Main menu display
│       └── errors/               # Error page templates
├── instance/
│   └── app.db                    # SQLite database
├── logs/
│   └── lunch_menu_app.log        # Application logs
├── config.py                     # Flask configuration
├── environment.yaml              # Conda environment specification
├── init_db.py                    # Database initialization
├── run.py                        # Application entry point
├── manual_scrape.py              # Manual scraping trigger
├── test_scraper.py               # Scraper testing utilities
├── test_db.py                    # Database testing
├── diagnose_db_issue.py          # Database diagnostics
├── analyze_*.py                  # Website analysis tools
├── CLAUDE.md                     # Development instructions
└── README.md                     # This file
```

## Architecture Overview

### Scraping Architecture
The scraping system uses an object-oriented design with the following patterns:

1. **Abstract Factory Pattern**: `BaseScraper` enforces consistent interface for all restaurant scrapers
2. **Service Layer**: `ScrapingService` orchestrates all scrapers and manages database operations
3. **Strategy Pattern**: Each scraper implements different strategies for various website formats

### Database Schema
- **Restaurant**: Stores restaurant metadata (name, URL, last_scraped timestamp)
- **MenuItem**: Stores individual menu items with date, category, description, and price
- **Relationship**: One Restaurant has many MenuItems with cascade delete

### Scraper Types by Format

#### HTML Scrapers
- **Erste Campus & 4oh4**: Extract from iframe content using Selenium
- **Enjoy Henry**: Parses HTML table with "today" column detection
- **Campus Bräu**: Navigates to SPEISEKARTE section, extracts weekly menu

#### PDF Scrapers
- **IKI Restaurant**: Downloads weekly lunch PDF, extracts text with PyPDF2
- **Albanco**: Downloads weekly PDF (KW pattern), parses Italian menu items

### Real-time Features
- **WebSocket Communication**: Socket.IO enables real-time menu updates
- **Client Notifications**: Automatic browser updates when new menus are scraped
- **Background Processing**: Non-blocking scraping with APScheduler

## Getting Started

### Prerequisites
- Python 3.11+
- Conda package manager
- Chrome browser (for Selenium WebDriver)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd lunch_app

# Create conda environment
conda env create -f environment.yaml
conda activate lunch-menu-app

# Initialize database
python init_db.py

# Run the application
python run.py
```

### Development Commands
```bash
# Test individual scrapers
python test_scraper.py
python test_scraper_standalone.py

# Test database operations
python test_db.py

# Manual scraping (useful in debug mode)
python manual_scrape.py

# Database diagnostics
python diagnose_db_issue.py

# Website analysis tools
python analyze_erste_campus.py
python analyze_4oh4.py
python analyze_henry.py
python analyze_iki.py
python analyze_cafegeorge.py
python analyze_campusbraeu.py
python analyze_albanco.py
```

### Configuration
The application uses environment-specific configuration in `config.py`:
- **Development**: Debug mode enabled, extensive logging
- **Production**: Security features enabled, optimized logging

Key settings:
- Daily scraping scheduled for 5:00 AM
- Rate limiting: 200 requests/day, 50 requests/hour
- Database: SQLite with file rotation logging
- Session security with HTTPOnly, SameSite cookies

## API Endpoints
- `GET /` - Main menu display page
- WebSocket events:
  - `menu_update` - Broadcasts menu updates to all connected clients

## Database Management
The application uses SQLAlchemy ORM with the following models:
- `Restaurant(id, name, url, last_scraped)`
- `MenuItem(id, restaurant_id, menu_date, category, description, price)`

## Security Features
- Flask-Limiter for rate limiting
- Secure session configuration
- Input validation in scrapers
- Environment-based secrets management
- Comprehensive error handling and logging

## Monitoring & Logging
- Structured logging with rotation
- Scraping statistics and success/failure tracking
- Database operation monitoring
- WebSocket connection tracking

## Deployment Notes
- Designed for Raspberry Pi deployment
- Uses SQLite for simplicity and low resource usage
- Conda environment for consistent dependencies
- APScheduler for reliable background task execution

## License
This project is licensed under the terms of the LICENSE file.

## Contributing
1. Add new scrapers by extending `BaseScraper`
2. Update `ScrapingService` to include new scrapers
3. Test with analysis scripts before integration
4. Follow existing patterns for error handling and logging