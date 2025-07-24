# Raspberry Pi Lunch Menu Aggregator - Development Plan

## Project Overview
A Python-based web application running on Raspberry Pi that automatically scrapes daily lunch menus from 5 restaurant websites (including a PDF-based weekly menu) and displays them in a modern, responsive interface.

## Architecture Design

### Technology Stack
- **Backend**: Python 3.9+ with Flask
- **Real-time Updates**: Socket.IO
- **Web Scraping**: BeautifulSoup4 + Requests (or Selenium for dynamic content)
- **Task Scheduling**: APScheduler
- **Database**: SQLite (lightweight for Pi)
- **Frontend**: HTML5, CSS3 (with CSS Grid/Flexbox), JavaScript
- **Caching**: Redis (optional) or file-based caching

### System Architecture
```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Scheduler     │────▶│  Web Scraper │────▶│   Database  │
│  (APScheduler)  │     │  (BS4/Selenium)    │   (SQLite)  │
└─────────────────┘     └──────────────┘     └─────────────┘
                                                    │
┌─────────────────┐     ┌──────────────┐            │
│   Web Client    │◀────│  Flask App   │◀───────────┘
│  (Browser)      │     │  + Socket.IO │
└─────────────────┘     └──────────────┘
```

## Phase 1: Environment Setup (Day 1)

### 1.1 Raspberry Pi Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y 

# Install Python and development tools
sudo apt install python3-pip python3-venv git nginx -y

# Install Chrome/Chromium for Selenium (if needed)
sudo apt install chromium-browser chromium-chromedriver -y
```

### 1.2 Project Structure
```
lunch-menu-aggregator/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py  # Abstract base class
│   ├── erste_campus.py   # Scraper for erstecampus.at
│   ├── four_oh_four.py   # Scraper for 4oh4.at
│   ├── enjoy_henry.py    # Scraper for enjoyhenry.com
│   ├── campus_braeu.py   # Scraper for campusbraeu.at
│   └── flipsnack_menu.py # Scraper for Flipsnack weekly menu
├── models/
│   ├── __init__.py
│   └── menu.py          # Database models
├── static/
│   ├── css/
│   │   └── style.css    # Modern styling
│   ├── js/
│   │   └── app.js       # Socket.IO client
│   └── images/
├── templates/
│   ├── base.html
│   └── index.html       # Main menu display
├── utils/
│   ├── __init__.py
│   ├── scheduler.py     # Task scheduling
│   └── cache.py         # Caching utilities
└── tests/
    └── test_scrapers.py # Unit tests
```

### 1.3 Virtual Environment Setup
```bash
cd ~/lunch-menu-aggregator
python3 -m venv venv
source venv/bin/activate
```

## Phase 2: Core Development (Days 2-4)

### 2.1 Dependencies Installation
Create `requirements.txt`:
```
Flask==3.0.0
Flask-SocketIO==5.3.5
Flask-SQLAlchemy==3.1.1
beautifulsoup4==4.12.2
requests==2.31.0
selenium==4.15.2
APScheduler==3.10.4
python-socketio==5.10.0
lxml==4.9.3
python-dateutil==2.8.2
```

### 2.2 Base Scraper Class
```python
# scrapers/base_scraper.py
from abc import ABC, abstractmethod
from datetime import datetime
import logging

class BaseScraper(ABC):
    def __init__(self, restaurant_name, url):
        self.restaurant_name = restaurant_name
        self.url = url
        self.logger = logging.getLogger(f"{__name__}.{restaurant_name}")
    
    @abstractmethod
    def scrape(self):
        """Returns dict with menu items"""
        pass
    
    def validate_data(self, data):
        """Validate scraped data structure"""
        required_fields = ['date', 'items']
        return all(field in data for field in required_fields)
```

### 2.3 Database Model
```python
# models/menu.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # soup, main, dessert, etc.
    item_name = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'restaurant': self.restaurant,
            'category': self.category,
            'item_name': self.item_name,
            'price': self.price,
            'date': self.date.isoformat()
        }
```

### 2.4 Individual Scrapers Implementation

Each scraper will need custom parsing logic based on the website structure:

```python
# Example: scrapers/erste_campus.py
from bs4 import BeautifulSoup
import requests
from .base_scraper import BaseScraper

class ErsteCampusScraper(BaseScraper):
    def __init__(self):
        super().__init__("Erste Campus", "https://erstecampus.at/en/kantine-am-campus-menu/")
    
    def scrape(self):
        try:
            response = requests.get(self.url, timeout=10)
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Parse menu items (customize based on actual HTML structure)
            menu_data = {
                'date': datetime.now().date(),
                'items': {
                    'soup': self._extract_soup(soup),
                    'main_dish': self._extract_main(soup),
                    'dessert': self._extract_dessert(soup)
                }
            }
            return menu_data
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            return None
```

### 2.5 Special Handler for Flipsnack PDF Menu

The Flipsnack menu requires special handling as it's a PDF viewer:

```python
# scrapers/flipsnack_menu.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import PyPDF2
import requests
import io
import re
from .base_scraper import BaseScraper

class FlipsnackMenuScraper(BaseScraper):
    def __init__(self):
        super().__init__("Weekly Menu", "https://www.flipsnack.com/EE9BE6CC5A8/wochenmen-14-20-08-2023.html")
    
    def scrape(self):
        """
        Two approaches for Flipsnack:
        1. Use Selenium to extract text from the embedded viewer
        2. Find and download the source PDF directly
        """
        try:
            # Option 1: Selenium approach
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            driver.get(self.url)
            
            # Wait for Flipsnack to load
            wait = WebDriverWait(driver, 20)
            
            # Try to find PDF download link or extract text
            # Flipsnack often has a download button
            try:
                download_btn = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "fs-download-btn"))
                )
                pdf_url = download_btn.get_attribute('href')
                
                # Download and parse PDF
                return self._parse_pdf_from_url(pdf_url)
                
            except:
                # Fallback: Try to extract visible text from pages
                return self._extract_from_flipsnack_viewer(driver)
                
        except Exception as e:
            self.logger.error(f"Flipsnack scraping failed: {e}")
            return None
        finally:
            if 'driver' in locals():
                driver.quit()
    
    def _parse_pdf_from_url(self, pdf_url):
        """Download and parse PDF content"""
        response = requests.get(pdf_url)
        pdf_file = io.BytesIO(response.content)
        
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        menu_data = {
            'date': datetime.now().date(),
            'items': {}
        }
        
        # Extract text from each page
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            # Parse daily menus from text
            daily_menus = self._parse_menu_text(text)
            menu_data['items'].update(daily_menus)
        
        return menu_data
    
    def _parse_menu_text(self, text):
        """Parse menu items from PDF text"""
        # This will need customization based on PDF structure
        # Example pattern matching for daily menus
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        menus = {}
        
        for day in days:
            # Find menu sections for each day
            day_pattern = rf'{day}.*?(?={"|".join(days)}|$)'
            day_match = re.search(day_pattern, text, re.DOTALL | re.IGNORECASE)
            
            if day_match:
                day_text = day_match.group()
                menus[day.lower()] = self._extract_dishes_from_text(day_text)
        
        return menus
```

### 2.6 Updated Requirements for PDF Handling

Add these to `requirements.txt`:
```
PyPDF2==3.0.1
pdfplumber==0.10.3  # Alternative PDF parser
selenium==4.15.2
webdriver-manager==4.0.1  # Automatic chromedriver management
```

## Phase 3: Flask Application (Days 5-6)

### 3.1 Main Application Structure
```python
# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from models.menu import db, MenuItem
from utils.scheduler import setup_scheduler
import config

app = Flask(__name__)
app.config.from_object(config)
socketio = SocketIO(app, cors_allowed_origins="*")
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    # Send current menu data on connection
    menus = get_today_menus()
    emit('menu_update', menus)

@socketio.on('request_update')
def handle_update_request():
    # Trigger manual update
    update_all_menus()
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    setup_scheduler(app)
    socketio.run(app, host='0.0.0.0', port=5000)
```

### 3.2 Scheduler Configuration
```python
# utils/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from scrapers import all_scrapers

def setup_scheduler(app):
    scheduler = BackgroundScheduler()
    
    # Schedule daily scraping at 10:30 AM
    scheduler.add_job(
        func=scrape_all_menus,
        trigger="cron",
        hour=10,
        minute=30,
        id='daily_menu_scrape'
    )
    
    # Initial scrape on startup
    scheduler.add_job(
        func=scrape_all_menus,
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=10)
    )
    
    scheduler.start()
```

## Phase 4: Frontend Development (Days 7-8)

### 4.1 Modern HTML Template
```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Lunch Menus</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
    <header>
        <h1>Today's Lunch Menus</h1>
        <div class="date">{{ current_date }}</div>
    </header>
    
    <main class="menu-grid">
        <!-- Menu cards will be dynamically inserted here -->
    </main>
    
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
```

### 4.2 Modern CSS Styling
```css
/* static/css/style.css */
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --accent-color: #e74c3c;
    --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #f5f7fa;
    min-height: 100vh;
}

.menu-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
}

.menu-card {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.menu-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0,0,0,0.15);
}

.restaurant-name {
    font-size: 1.5rem;
    font-weight: bold;
    background: var(--bg-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.5rem;
}

.menu-category {
    margin-bottom: 1rem;
}

.category-label {
    font-weight: 600;
    color: var(--primary-color);
    text-transform: uppercase;
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
}

.menu-item {
    padding: 0.5rem 0;
    border-bottom: 1px solid #e0e0e0;
}

.loading-spinner {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Weekly Menu Tabs */
.tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
    border-bottom: 2px solid #e0e0e0;
}

.tab-btn {
    padding: 0.75rem 1.5rem;
    border: none;
    background: none;
    cursor: pointer;
    font-weight: 600;
    color: #666;
    transition: all 0.3s ease;
    border-bottom: 3px solid transparent;
}

.tab-btn:hover {
    color: var(--secondary-color);
}

.tab-btn.active {
    color: var(--secondary-color);
    border-bottom-color: var(--secondary-color);
}

.day-menu {
    display: none;
}

.day-menu.active {
    display: block;
}

/* PDF Notice */
.pdf-notice {
    background: #fff3cd;
    color: #856404;
    padding: 0.75rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    font-size: 0.875rem;
}
```

### 4.3 Socket.IO Client
```javascript
// static/js/app.js
const socket = io();

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('menu_update', (data) => {
    updateMenuDisplay(data);
});

function updateMenuDisplay(menus) {
    const menuGrid = document.querySelector('.menu-grid');
    menuGrid.innerHTML = '';
    
    menus.forEach(restaurant => {
        const card = createMenuCard(restaurant);
        menuGrid.appendChild(card);
    });
}

function createMenuCard(restaurant) {
    const card = document.createElement('div');
    card.className = 'menu-card';
    
    // Handle weekly menus differently
    if (restaurant.name === 'Weekly Menu') {
        card.innerHTML = `
            <h2 class="restaurant-name">${restaurant.name}</h2>
            <div class="weekly-menu-tabs">
                ${createWeeklyMenuTabs(restaurant.items)}
            </div>
        `;
    } else {
        card.innerHTML = `
            <h2 class="restaurant-name">${restaurant.name}</h2>
            ${createMenuItems(restaurant.items)}
        `;
    }
    
    return card;
}

function createWeeklyMenuTabs(weeklyItems) {
    // Create tabbed interface for weekly menu
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
    let tabsHTML = '<div class="tabs">';
    
    days.forEach((day, index) => {
        tabsHTML += `
            <button class="tab-btn ${index === 0 ? 'active' : ''}" 
                    onclick="showDay('${day}')">${day.charAt(0).toUpperCase() + day.slice(1)}</button>
        `;
    });
    
    tabsHTML += '</div><div class="tab-content">';
    
    days.forEach((day, index) => {
        tabsHTML += `
            <div class="day-menu ${index === 0 ? 'active' : ''}" id="${day}-menu">
                ${createMenuItems(weeklyItems[day] || {})}
            </div>
        `;
    });
    
    return tabsHTML + '</div>';
}
```

## Phase 5: Testing & Deployment (Days 9-10)

### 5.1 Testing Strategy
1. **Unit Tests**: Test each scraper individually
2. **Integration Tests**: Test database operations
3. **End-to-End Tests**: Test full scraping → storage → display flow

### 5.2 Error Handling
- Implement retry logic for failed scrapes
- Store last successful scrape data
- Email/notification alerts for persistent failures

### 5.3 Performance Optimization
- Implement caching for static resources
- Use connection pooling for database
- Optimize scraping with concurrent requests

### 5.4 Deployment on Raspberry Pi
```bash
# Set up systemd service
sudo nano /etc/systemd/system/lunch-menu.service

[Unit]
Description=Lunch Menu Aggregator
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/lunch-menu-aggregator
Environment="PATH=/home/pi/lunch-menu-aggregator/venv/bin"
ExecStart=/home/pi/lunch-menu-aggregator/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5.5 Nginx Configuration
```nginx
server {
    listen 80;
    server_name lunch.local;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Phase 6: Advanced Features (Optional)

### 6.1 Additional Features
- **Multi-language Support**: Detect and translate menu items
- **Price Tracking**: Historical price analysis
- **Dietary Filters**: Vegetarian, vegan, gluten-free options
- **Mobile App**: Progressive Web App (PWA) support
- **API Endpoints**: RESTful API for external access

### 6.2 Monitoring & Analytics
- Implement logging with rotation
- Track scraping success rates
- Monitor system resources on Pi

## Special Considerations for Flipsnack PDF Menu

### PDF Handling Challenges
1. **Dynamic Loading**: Flipsnack loads content dynamically, requiring Selenium
2. **URL Changes**: The Flipsnack URL may change weekly - implement URL pattern detection
3. **PDF Extraction**: Two approaches:
   - Direct PDF download if available
   - OCR fallback for image-based PDFs

### Implementation Strategy
```python
# config.py - Add Flipsnack configuration
FLIPSNACK_CONFIG = {
    'base_url': 'https://www.flipsnack.com/',
    'publication_pattern': r'wochenmen.*\.html',
    'retry_attempts': 3,
    'pdf_parse_method': 'pypdf2'  # or 'pdfplumber' or 'ocr'
}
```

### Weekly Menu Display
- Implement tabbed interface for Monday-Friday
- Cache weekly menu to reduce PDF parsing
- Add "Last Updated" timestamp for weekly menus

## Maintenance & Best Practices

### Security Considerations
1. Use environment variables for sensitive data
2. Implement rate limiting for scraping
3. Add CORS protection
4. Regular security updates

### Code Quality
1. Follow PEP 8 style guide
2. Type hints for better code clarity
3. Comprehensive docstrings
4. Regular code reviews

### Backup Strategy
1. Daily database backups
2. Configuration version control
3. Automated backup to cloud storage

## Timeline Summary
- **Days 1-2**: Environment setup and project structure
- **Days 3-4**: Scraper development for 5 restaurants (including PDF handler)
- **Days 5-6**: Flask application and Socket.IO integration
- **Days 7-8**: Frontend development with weekly menu tabs
- **Days 9-10**: Testing, optimization, and deployment

## Next Steps
1. Analyze each restaurant website's HTML structure
2. Test Flipsnack PDF extraction methods
3. Implement robust error handling
4. Create comprehensive documentation
5. Set up monitoring and alerting
6. Plan for scalability and maintenance
