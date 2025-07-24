#!/bin/bash
# Initialize Lunch Menu Aggregator Project Structure

echo "==================================================="
echo "  Lunch Menu Aggregator - Project Initialization"
echo "==================================================="

# Create project directory structure
echo "Creating project directories..."

mkdir -p scrapers
mkdir -p models
mkdir -p utils
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p templates
mkdir -p tests
mkdir -p logs
mkdir -p docs
mkdir -p scripts

# Create __init__.py files
echo "Creating __init__.py files..."

touch scrapers/__init__.py
touch models/__init__.py
touch utils/__init__.py
touch tests/__init__.py

# Create placeholder files
echo "Creating placeholder files..."

# Create basic HTML template
cat > templates/base.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Lunch Menu Aggregator{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
EOF

# Create index template placeholder
cat > templates/index.html << 'EOF'
{% extends "base.html" %}

{% block content %}
<header>
    <h1>Today's Lunch Menus</h1>
    <div class="date">{{ current_date }}</div>
    <button id="refresh-btn" class="refresh-button">🔄 Refresh</button>
</header>

<main class="menu-grid" id="menu-container">
    <!-- Menu cards will be dynamically inserted here -->
    <div class="loading">Loading menus...</div>
</main>
{% endblock %}
EOF

# Create basic CSS
cat > static/css/style.css << 'EOF'
/* Basic styling - replace with the full version from the plan */
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

header {
    background: white;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.menu-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
}

.loading {
    text-align: center;
    padding: 4rem;
    color: #666;
}
EOF

# Create basic JS
cat > static/js/app.js << 'EOF'
// Basic Socket.IO setup - replace with the full version from the plan
const socket = io();

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('menu_update', (data) => {
    console.log('Menu update received:', data);
    // TODO: Update menu display
});

document.getElementById('refresh-btn').addEventListener('click', () => {
    socket.emit('request_update');
});
EOF

# Create scrapers __init__.py with imports
cat > scrapers/__init__.py << 'EOF'
"""
Scrapers package initialization
"""

from typing import List, Type
from .base_scraper import BaseScraper

# Import all scraper classes here after implementing them
# from .erste_campus import ErsteCampusScraper
# from .four_oh_four import FourOhFourScraper
# from .enjoy_henry import EnjoyHenryScraper
# from .campus_braeu import CampusBraeuScraper
# from .flipsnack_menu import FlipsnackMenuScraper

def get_all_scrapers() -> List[Type[BaseScraper]]:
    """Get all available scraper classes"""
    return [
        # ErsteCampusScraper,
        # FourOhFourScraper,
        # EnjoyHenryScraper,
        # CampusBraeuScraper,
        # FlipsnackMenuScraper,
    ]

def run_all_scrapers():
    """Run all scrapers and save results to database"""
    # TODO: Implement this function
    pass
EOF

# Create base scraper template
cat > scrapers/base_scraper.py << 'EOF'
"""
Base scraper class for all restaurant scrapers
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging
from typing import Dict, Optional, Any

class BaseScraper(ABC):
    """Abstract base class for all scrapers"""

    def __init__(self, restaurant_name: str, url: str):
        self.restaurant_name = restaurant_name
        self.url = url
        self.logger = logging.getLogger(f"{__name__}.{restaurant_name}")

    @abstractmethod
    def scrape(self) -> Optional[Dict[str, Any]]:
        """
        Scrape menu data from the restaurant website

        Returns:
            Dictionary with menu data or None if scraping failed
            Expected format:
            {
                'date': datetime.date,
                'items': {
                    'category': 'item_name' or {'name': 'item', 'price': 10.50}
                }
            }
        """
        pass

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate scraped data structure"""
        required_fields = ['date', 'items']
        return all(field in data for field in required_fields)
EOF

# Create utils __init__.py
cat > utils/__init__.py << 'EOF'
"""
Utilities package
"""
EOF

# Create scheduler placeholder
cat > utils/scheduler.py << 'EOF'
"""
Task scheduler for automated scraping
"""

from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)

def setup_scheduler(app, socketio):
    """Set up the APScheduler for automated scraping"""
    scheduler = BackgroundScheduler()

    # TODO: Add scheduled jobs

    scheduler.start()
    logger.info("Scheduler started")

    return scheduler
EOF

# Create cache utilities placeholder
cat > utils/cache.py << 'EOF'
"""
Caching utilities
"""

def cache_key_prefix():
    """Generate cache key prefix based on date"""
    from datetime import datetime
    return f"menu_{datetime.now().date()}"
EOF

# Create pytest configuration
cat > tests/conftest.py << 'EOF'
"""
Pytest configuration and fixtures
"""

import pytest
from app import create_app
from models.menu import db

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
dist/
build/

# Conda
conda-meta/

# Flask
instance/
.webassets-cache

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Documentation
docs/_build/

# Temporary files
*.tmp
*.bak
*~
EOF

# Create README
cat > README.md << 'EOF'
# Lunch Menu Aggregator

A Python-based web application that automatically scrapes daily lunch menus from multiple restaurant websites and displays them in a modern, responsive interface.

## Features

- Automated daily menu scraping
- Real-time updates via Socket.IO
- Modern responsive UI
- Support for PDF-based menus
- Caching for performance
- RESTful API endpoints

## Setup

1. Install Conda environment:
   ```bash
   conda env create -f environment.yaml
   conda activate lunch-menu-app
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Initialize database:
   ```bash
   python scripts/setup_db.py
   ```

4. Run development server:
   ```bash
   python app.py
   ```

## Testing

Run tests with:
```bash
pytest
```

## Documentation

See the `docs/` directory for detailed documentation.
EOF

# Set execute permissions for scripts
chmod +x scripts/*.py
chmod +x init_project.sh

echo ""
echo "✅ Project structure created successfully!"
echo ""
echo "Next steps:"
echo "1. Create/activate conda environment: conda env create -f environment.yaml"
echo "2. Copy .env.example to .env and configure"
echo "3. Initialize database: python scripts/setup_db.py"
echo "4. Start implementing scrapers in the scrapers/ directory"
echo "5. Run the development server: python app.py"
echo ""
echo "Happy coding! 🚀"
