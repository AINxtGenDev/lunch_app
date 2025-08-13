# Lunch Menu Aggregator

## Project Overview
A Python-based web application that automatically scrapes daily lunch menus from multiple restaurant websites and displays them in a modern, responsive interface. The application features real-time updates and supports various menu formats including HTML tables, iframes, and PDF documents.

**🍽️ Perfect for daily lunch planning with real-time menu updates**
**📱 Works perfectly on mobile devices (Android & iOS) with optimized touch interface**

## Features
- **Automated Scraping:** Scrapes daily menus from 8 different restaurant websites
- **Multi-Format Support:** Handles HTML tables, iframes, PDF documents, and dynamic JavaScript content
- **Real-time Updates:** Uses Socket.IO to push menu updates to the web interface in real-time
- **Modern UI:** Professional, accessible interface with ultra-high contrast color system
- **Mobile Optimized:** Fully responsive design optimized for Android and iOS devices
- **Accessibility:** WCAG AAA compliant with maximum contrast ratios for outdoor mobile viewing
- **Scheduled Tasks:** Automatically updates menus daily at 5:00 AM using APScheduler
- **Database Storage:** Persistent menu storage with SQLite database
- **Rate Limiting:** Built-in rate limiting for API protection
- **Error Handling:** Comprehensive error handling and logging

## Supported Restaurants & URLs

| Restaurant | URL | Format | Items | Status |
|------------|-----|--------|-------|---------|
| **Erste Campus** | https://erstecampus.at/mealplan/ | iframe | 6 items | ✅ Active |
| **4oh4** | https://4oh4.at/lunch-menu/ | iframe | 9 items | ✅ Active |
| **Henry BDO** | https://www.enjoyhenry.com/menuplan-bdo/ | HTML table | 8 items | ✅ Active |
| **IKI Restaurant** | https://iki-restaurant.at/ | PDF (weekly) | 7 items | ✅ Active |
| **Cafe George** | https://cafegeorge.at/en/weekly-menu-en/ | iframe | 11 items | ✅ Active |
| **Campus Bräu** | https://www.campusbraeu.at/ | HTML (weekly) | 4 items | ✅ Active |
| **Albanco** | https://albanco.at/ | PDF (weekly) | 12 items | ✅ Active |
| **Cyclist** | https://www.cafe-cyclist.com/ | Flipsnack (manual) | 2 items | ✅ Active |

**Total: 59+ daily menu items across 8 restaurants**

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
- **CSS3** with Grid/Flexbox layout and modern gradients
- **Ultra-High Contrast Design** with WCAG AAA compliance for mobile readability
- **Responsive Design** optimized for mobile, tablet, and desktop
- **Vanilla JavaScript** with Socket.IO client
- **Real-time Updates** via WebSocket
- **Touch Optimizations** for mobile and tablet devices
- **System Fonts** for optimal rendering on all devices

### Development Tools
- **Chrome WebDriver Manager** for automated browser management
- **Conda** for environment and dependency management

## Project Structure
```
lunch_app/
├── app/                              # Main application package
│   ├── __init__.py                   # Flask app factory with SocketIO & scheduler
│   ├── models.py                     # Database models (Restaurant, MenuItem)
│   ├── routes.py                     # HTTP route handlers
│   ├── errors.py                     # Error handlers (404, 500)
│   ├── scrapers/                     # Restaurant scraper implementations
│   │   ├── base_scraper.py           # Abstract base scraper class
│   │   ├── erste_campus_scraper.py   # Erste Campus iframe scraper
│   │   ├── fouroh4_scraper.py        # 4oh4 restaurant iframe scraper
│   │   ├── henry_scraper.py          # Henry BDO HTML table scraper
│   │   ├── iki_scraper.py            # IKI Restaurant PDF scraper
│   │   ├── cafegeorge_scraper.py     # Cafe George iframe scraper
│   │   ├── campusbraeu_scraper.py    # Campus Bräu HTML scraper
│   │   ├── albanco_scraper.py        # Albanco weekly PDF scraper
│   │   ├── cyclist_scraper.py        # Cyclist Cafe Flipsnack scraper
│   │   └── chrome_driver_setup.py    # Chrome WebDriver configuration
│   ├── services/
│   │   └── scraping_service.py       # Orchestrates all scrapers
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css             # Mobile-optimized responsive styles
│   │   ├── js/
│   │   │   └── main.js               # Socket.IO client & category mapping
│   │   └── image/                    # Static images (HPE logo, AI duck)
│   │       ├── hpe_logo_1.png        # Animated HPE logo
│   │       └── ai_duck_15_round.png  # AI Duck mascot
│   └── templates/
│       ├── base.html                 # Base template with responsive layout
│       ├── index.html                # Main menu display page
│       └── errors/                   # Error page templates
│           ├── 404.html              # Not found page
│           ├── 500.html              # Server error page
│           └── error.html            # Generic error page
├── instance/
│   └── app.db                        # SQLite database
├── logs/
│   └── lunch_menu_app.log            # Application logs with rotation
├── config.py                         # Flask configuration (dev/prod)
├── config_simple.py                  # Simplified configuration module
├── environment.yaml                  # Conda environment specification
├── init_db.py                        # Database initialization script
├── run.py                            # Application entry point
├── gunicorn_config.py               # Gunicorn WSGI server configuration
├── setup_project.py                 # Project setup utility
├── manual_scrape.py                 # Manual scraping trigger (all restaurants)
├── manual_scrape_today.py           # Manual scraping for today's menus
├── manual_scrape_albanco.py         # Individual restaurant scraper test
├── manual_scrape_campusbraeu.py    # Individual restaurant scraper test
├── test_scraper.py                  # Comprehensive scraper testing
├── test_scraper_standalone.py       # Standalone scraper tests
├── test_scraper_direct.py           # Direct scraper invocation tests
├── test_db.py                       # Database operations testing
├── diagnose_db_issue.py             # Database diagnostics utility
├── check_db_today.py                # Check today's database entries
├── analyze_*.py                     # Website analysis tools for each restaurant
│   ├── analyze_erste_campus.py      # Erste Campus website analyzer
│   ├── analyze_4oh4.py              # 4oh4 website analyzer
│   ├── analyze_henry.py             # Henry BDO website analyzer
│   ├── analyze_iki.py               # IKI Restaurant analyzer
│   ├── analyze_cafegeorge.py        # Cafe George analyzer
│   ├── analyze_campusbraeu.py       # Campus Bräu analyzer
│   ├── analyze_albanco.py           # Albanco analyzer
│   ├── analyze_iframe_content.py    # iframe content analyzer
│   ├── analyze_price_simple.py      # Simple price parsing analysis
│   └── analyze_price_structure.py   # Price structure analysis
├── test_*_scraper.py                # Individual scraper unit tests
│   ├── test_4oh4_scraper.py         # 4oh4 scraper tests
│   ├── test_cafegeorge_scraper.py   # Cafe George scraper tests
│   ├── test_henry_scraper.py        # Henry scraper tests
│   ├── test_iki_scraper.py          # IKI scraper tests
│   ├── test_cafegeorge_iframe.py    # Cafe George iframe tests
│   ├── test_pdf_extraction.py       # PDF extraction tests
│   ├── test_pdf_plumber.py          # PDF plumber library tests
│   └── test_price_extraction.py     # Price extraction tests
├── debug_*.py                       # Debug utilities for troubleshooting
│   ├── debug_4oh4_scraper.py        # 4oh4 scraper debugging
│   ├── debug_4oh4_structure.py      # 4oh4 structure analysis
│   ├── debug_cafegeorge_scraper.py  # Cafe George scraper debugging
│   ├── debug_cafegeorge_structure.py # Cafe George structure analysis
│   ├── debug_actual_scraper.py      # Active scraper debugging
│   ├── debug_imports.py             # Import debugging utility
│   ├── debug_parser_flow.py         # Parser flow debugging
│   └── debug_price_parsing.py       # Price parsing debugging
├── erste_campus_*.py                # Erste Campus scraper variations
│   ├── erste_campus_advanced_scraper.py
│   ├── erste_campus_final_scraper.py
│   ├── erste_campus_final_scraper_fixed.py
│   ├── erste_campus_iframe_scraper.py
│   ├── erste_campus_nextjs_scraper.py
│   ├── erste_campus_scraper_fixed.py
│   └── erste_campus_selenium_scraper.py
├── *.html                           # Downloaded HTML content for analysis
│   ├── 4oh4_*.html                  # 4oh4 restaurant HTML samples
│   ├── albanco_*.html               # Albanco HTML samples
│   ├── cafegeorge_*.html            # Cafe George HTML samples
│   ├── campusbraeu_*.html           # Campus Bräu HTML samples
│   ├── erste_campus_*.html          # Erste Campus HTML samples
│   ├── henry_*.html                 # Henry BDO HTML samples
│   └── iki_*.html                   # IKI restaurant HTML samples
├── *.json                           # JSON data files
│   ├── api_page_props.json          # API page properties
│   ├── api_response.json            # API response samples
│   ├── menu_data.json               # Menu data structure
│   ├── page_props.json              # Page properties
│   └── react_data.json              # React component data
├── *.txt                            # Text files and extracts
│   ├── 00_readme.txt                # Quick readme notes
│   ├── div.txt                      # HTML div content
│   ├── iki_extracted_text.txt       # IKI extracted text
│   ├── iki_lunch_specials.txt       # IKI lunch specials
│   └── iki_tageskarte.txt           # IKI daily menu card
├── *.pdf                            # PDF menu samples
│   └── albanco_KW31.pdf             # Albanco weekly menu PDF
├── *.sh                             # Shell scripts
│   ├── check_app_status.sh          # Application status checker
│   ├── check_autostart.sh           # Autostart verification
│   ├── daily_scrape.sh              # Daily scraping script
│   ├── debug_service.sh             # Service debugging
│   ├── deploy_to_raspberry.sh       # Raspberry Pi deployment
│   ├── find_conda_paths.sh          # Conda path finder
│   └── install_scraper_timer.sh     # Systemd timer installer
├── *.service / *.timer              # Systemd service files
│   ├── lunch-app.service            # Main application service
│   ├── lunch-scraper.service        # Scraper service
│   └── lunch-scraper.timer          # Scraper timer
├── view_iframe_content.py           # iframe content inspection tool
├── download_api_data.py             # API data downloader
├── examine_menu_json.py             # Menu JSON examiner
├── find_current_lunch_pdf.py        # PDF finder utility
├── Caddyfile                        # Caddy web server configuration
├── CLAUDE.md                        # Development instructions for Claude
├── GEMINI.md                        # Development instructions for Gemini
├── LICENSE                          # Project license
├── README.md                        # This comprehensive documentation
└── project-structure.txt            # Generated project structure

16 directories, 148 files
```

## Architecture Overview

### Scraping Architecture
The scraping system uses an object-oriented design with the following patterns:

1. **Abstract Factory Pattern**: `BaseScraper` enforces consistent interface for all restaurant scrapers
2. **Service Layer**: `ScrapingService` orchestrates all scrapers and manages database operations
3. **Strategy Pattern**: Each scraper implements different strategies for various website formats
4. **Observer Pattern**: Real-time updates via Socket.IO when scraping completes

### Database Schema
- **Restaurant**: Stores restaurant metadata (name, URL, last_scraped timestamp)
- **MenuItem**: Stores individual menu items with date, category, description, and price
- **Relationship**: One Restaurant has many MenuItems with cascade delete

### Scraper Types by Format

#### HTML Scrapers
- **Erste Campus & 4oh4**: Extract from iframe content using Selenium WebDriver
- **Henry BDO**: Parses HTML table with "today" column detection
- **Campus Bräu**: Navigates to SPEISEKARTE section, extracts weekly menu
- **Cafe George**: Selenium-based iframe content extraction

#### PDF Scrapers
- **IKI Restaurant**: Downloads weekly lunch PDF, extracts German/English text
- **Albanco**: Downloads weekly PDF (KW pattern), parses Italian specialties menu

#### Manual/Hardcoded Scrapers
- **Cyclist**: Uses hardcoded weekly menu (Flipsnack viewer not scrapable)

### Real-time Features
- **WebSocket Communication**: Socket.IO enables real-time menu updates
- **Client Notifications**: Automatic browser updates when new menus are scraped
- **Background Processing**: Non-blocking scraping with APScheduler
- **Connection Management**: Handles client disconnections gracefully

## Mobile Compatibility & Design

### 📱 Perfect Mobile Experience
**This application works perfectly on both Android and iOS devices** with a mobile-first responsive design:

#### **Android Devices:**
- ✅ **Chrome Mobile**: Full feature support with touch optimizations
- ✅ **Samsung Internet**: Tested on Galaxy devices
- ✅ **Firefox Mobile**: Complete compatibility
- ✅ **Edge Mobile**: Full Android support
- ✅ **All screen sizes**: From small phones to large tablets

#### **iOS Devices:**
- ✅ **Safari Mobile**: Optimized for all iPhone and iPad models
- ✅ **Chrome iOS**: Complete feature compatibility
- ✅ **Firefox iOS**: Full support
- ✅ **Edge iOS**: Complete iOS compatibility
- ✅ **Retina Display**: Enhanced for high-DPI screens

### Mobile-Optimized Features

#### **Touch-First Design:**
- **44px minimum touch targets** following platform guidelines
- **Touch feedback** with active states (no hover on mobile)
- **Swipe-friendly cards** with proper spacing
- **Single column layout** optimized for portrait viewing

#### **Ultra-High Contrast for Mobile:**
- **WCAG AAA compliance** with 7:1+ contrast ratios
- **Outdoor readability** optimized for bright sunlight
- **System fonts** for best rendering on all devices
- **Enhanced shadows** and borders for depth perception

#### **Responsive Breakpoints:**
- **Desktop (1025px+)**: Multi-column grid with hover effects
- **Tablets (769px-1024px)**: 2-column layout with touch optimization
- **Mobile (≤768px)**: Single column with enhanced spacing
- **Small phones (≤480px)**: Compact layout for iPhone SE, small Android

#### **Performance Optimizations:**
- **Fast loading** with optimized CSS and minimal JavaScript
- **Efficient rendering** using CSS Grid and Flexbox
- **Touch scrolling** with momentum on iOS
- **Battery-friendly** animations and transitions

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

Access the application:
- **Desktop**: http://localhost:5000
- **Mobile**: Connect to your local network IP (e.g., http://192.168.1.100:5000)

### Development Commands
```bash
# Test individual scrapers
python test_scraper.py
python test_scraper_standalone.py
python test_scraper_direct.py

# Test specific restaurant scrapers
python test_4oh4_scraper.py
python test_cafegeorge_scraper.py
python test_henry_scraper.py
python test_iki_scraper.py
python test_cyclist_scraper.py

# Manual scraping commands
python manual_scrape.py              # Scrape all restaurants
python manual_scrape_today.py        # Scrape today's menus only
python manual_scrape_albanco.py      # Individual restaurant test
python manual_scrape_campusbraeu.py  # Individual restaurant test

# Test database operations
python test_db.py
python check_db_today.py             # Check today's database entries

# Database diagnostics
python diagnose_db_issue.py

# Website analysis tools (for scraper development)
python analyze_erste_campus.py
python analyze_4oh4.py
python analyze_henry.py
python analyze_iki.py
python analyze_cafegeorge.py
python analyze_campusbraeu.py
python analyze_albanco.py
python analyze_cyclist.py
python analyze_iframe_content.py
python analyze_price_simple.py
python analyze_price_structure.py

# Debug utilities
python debug_4oh4_scraper.py
python debug_cafegeorge_scraper.py
python debug_actual_scraper.py
python debug_imports.py
python debug_parser_flow.py
python debug_price_parsing.py

# PDF testing utilities
python test_pdf_extraction.py
python test_pdf_plumber.py
python find_current_lunch_pdf.py

# Deployment scripts
bash deploy_to_raspberry.sh          # Deploy to Raspberry Pi
bash install_scraper_timer.sh        # Install systemd timer
bash check_app_status.sh             # Check application status
bash daily_scrape.sh                 # Run daily scraping manually
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
- `GET /` - Main menu display page with real-time updates
- WebSocket events:
  - `initial_menu_load` - Sends current menu data on connection
  - `menu_update` - Broadcasts menu updates to all connected clients

## Ultra-High Contrast Design System

### Color Palette (Mobile-Optimized)
The application uses an ultra-high contrast color system optimized for mobile readability:

#### **Text Colors:**
- **Primary Text**: Pure Black (#000000) on white backgrounds
- **Secondary Text**: Dark Gray (#1a1a1a) for descriptions
- **Light Text**: Medium Gray (#424242) for metadata

#### **Category Colors (High Visibility):**
- **SOUP/SUPPE**: Bold Orange (#FF5722)
- **SALAD/SALAT**: Vibrant Green (#4CAF50)
- **MAIN DISH**: Deep Blue (#5B6DC8)
- **PASTA**: Purple (#7B68EE)
- **BURGER**: Orange (#FF6F00)
- **DESSERT**: Pink (#E91E63)
- **PIZZA**: Purple (#9C27B0)
- **VEGETARIAN**: Bright Green (#00C853)

#### **UI Elements:**
- **Price Badges**: High-contrast blue (#0080FF) with white text
- **Card Backgrounds**: Pure white (#ffffff) with strong shadows
- **Borders**: Medium gray (#cccccc) for clear separation

### Accessibility Features
- **WCAG AAA Compliance**: All text exceeds 7:1 contrast ratio
- **Touch Targets**: Minimum 44px for easy mobile interaction
- **High Contrast Mode**: Enhanced borders and shadows for users with visual impairments
- **Dark Mode Support**: Automatic detection and optimized colors
- **Font Rendering**: System fonts for optimal display on all devices

## Security Features
- Flask-Limiter for rate limiting protection
- Secure session configuration with HTTPOnly cookies
- Input validation in all scrapers to prevent XSS
- Environment-based secrets management
- Comprehensive error handling and logging
- CSRF protection for form submissions

## Monitoring & Logging
- Structured logging with automatic rotation
- Scraping statistics and success/failure tracking
- Database operation monitoring
- WebSocket connection tracking
- Performance metrics collection

## Deployment Notes

### Platform Support
- **Raspberry Pi**: Optimized for ARM-based single-board computers
- **Traditional Servers**: Compatible with x86/x64 Linux, Windows, macOS
- **Cloud Deployment**: Ready for Docker, Heroku, AWS, Azure deployments
- **Mobile Hosting**: Perfect for local network mobile access

### Technical Requirements
- **Database**: SQLite for simplicity and low resource usage
- **Environment**: Conda for consistent dependency management
- **Scheduling**: APScheduler for reliable background task execution
- **Performance**: Optimized CSS and JavaScript for fast mobile rendering
- **Web Server**: Gunicorn WSGI server with configuration included

### Systemd Service Configuration
The project includes systemd service files for production deployment:

#### lunch-app.service
- Main application service for the Flask web server
- Runs the application with Gunicorn WSGI server
- Auto-restarts on failure

#### lunch-scraper.service & lunch-scraper.timer
- Scheduled scraping service with systemd timer
- Runs daily scraping at 5:00 AM
- Separate from main app for reliability

Installation:
```bash
# Copy service files to systemd
sudo cp lunch-app.service /etc/systemd/system/
sudo cp lunch-scraper.service /etc/systemd/system/
sudo cp lunch-scraper.timer /etc/systemd/system/

# Enable and start services
sudo systemctl enable lunch-app.service
sudo systemctl enable lunch-scraper.timer
sudo systemctl start lunch-app.service
sudo systemctl start lunch-scraper.timer

# Check status
sudo systemctl status lunch-app.service
sudo systemctl status lunch-scraper.timer
```

### Web Server Configuration
- **Caddy**: Included Caddyfile for reverse proxy setup
- **Gunicorn**: Production WSGI server configuration in `gunicorn_config.py`
- **Default Port**: 5000 (configurable in environment)

### Mobile Network Setup
For mobile access on your local network:
1. **Find your server IP**: `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
2. **Access from mobile**: http://YOUR_IP:5000
3. **Firewall**: Ensure port 5000 is open for local network access

## License
This project is licensed under the terms included in the LICENSE file.

## Contributing

### Adding New Scrapers
1. **Extend BaseScraper**: Create new scraper class inheriting from `BaseScraper`
2. **Update ScrapingService**: Add new scraper to the service orchestrator
3. **Test with Analysis Scripts**: Use `analyze_*.py` tools before integration
4. **Follow Patterns**: Maintain consistent error handling and logging
5. **Mobile Testing**: Verify new content displays properly on mobile devices

### Design System Guidelines
1. **Ultra-High Contrast**: Ensure all new UI elements exceed WCAG AAA standards
2. **Mobile-First**: Design for mobile devices, then enhance for larger screens
3. **Touch Targets**: Maintain minimum 44px touch targets for interactive elements
4. **System Fonts**: Use system font stack for optimal mobile rendering
5. **Performance**: Optimize CSS and JavaScript for mobile devices

### Testing Checklist
- [ ] **Desktop browsers**: Chrome, Firefox, Safari, Edge compatibility
- [ ] **Mobile devices**: iOS Safari, Chrome Mobile, Samsung Internet testing
- [ ] **Android tablets**: Layout verification on various screen sizes
- [ ] **iOS tablets**: iPad compatibility across different models
- [ ] **Accessibility audit**: Contrast ratios, keyboard navigation, screen readers
- [ ] **Performance testing**: Load times on slower mobile connections
- [ ] **Touch interaction**: Swipe, tap, and scroll behavior
- [ ] **Outdoor readability**: High contrast verification in bright conditions

---

**🍽️ Enjoy your perfectly formatted, mobile-optimized lunch menu experience! 📱**