# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup
```bash
# Create conda environment from environment.yaml
conda env create -f environment.yaml
conda activate lunch-menu-app

# Initialize database
python init_db.py

# Run the application
python run.py
```

### Running Tests
```bash
# Test individual scrapers
python test_scraper.py
python test_scraper_standalone.py

# Test database operations
python test_db.py
```

### Database Management
```bash
# Initialize/reset database
python init_db.py

# Diagnose database issues
python diagnose_db_issue.py
```

## Architecture Overview

### Flask Application Structure
The application follows a standard Flask pattern with the following key components:

- **Application Factory**: `app/__init__.py` contains `create_app()` which initializes Flask with extensions (SQLAlchemy, SocketIO, Limiter) and configures logging, database, and background scheduling
- **Configuration**: `config.py` defines environment-specific settings with security defaults
- **Database Models**: `app/models.py` defines Restaurant and MenuItem tables with SQLAlchemy ORM
- **Routes**: `app/routes.py` handles HTTP endpoints for the web interface
- **Real-time Updates**: Flask-SocketIO enables WebSocket communication for live menu updates

### Scraping Architecture
The scraping system uses an object-oriented design:

- **Base Scraper**: `app/scrapers/base_scraper.py` provides abstract base class with common database operations
- **Individual Scrapers**: Each restaurant has its own scraper class inheriting from BaseScraper (currently only `erste_campus_scraper.py` implemented)
- **Scraping Service**: `app/services/scraping_service.py` orchestrates all scrapers, handles scheduling, and manages WebSocket notifications
- **Scheduler**: APScheduler runs daily scraping at 5:00 AM

### Key Design Patterns
1. **Abstract Factory Pattern**: BaseScraper enforces consistent interface for all restaurant scrapers
2. **Service Layer**: ScrapingService encapsulates business logic and coordinates between scrapers and database
3. **Application Factory**: Allows flexible configuration and testing
4. **Background Jobs**: Non-blocking scraping with scheduled updates

### Security Considerations
- Flask-Limiter configured for rate limiting (200/day, 50/hour)
- Session security with HTTPOnly, SameSite cookies
- Environment-based configuration with `.env` file for secrets
- Logging with rotation to prevent disk space issues
- Input validation in scrapers to handle untrusted HTML content

### Database Schema
- **Restaurant**: Stores restaurant metadata (name, URL, last_scraped timestamp)
- **MenuItem**: Stores individual menu items with date, category, description, and price
- Relationship: One Restaurant has many MenuItems with cascade delete

### Debugging Tools
The codebase includes several standalone scripts for debugging:
- `erste_campus_*_scraper.py`: Various iterations of scraper development
- `analyze_*.py`: Tools for analyzing scraped content
- `view_iframe_content.py`: Inspect iframe content from websites