# setup_project.py
import os
import secrets

def setup_project():
    """Set up the project structure and configuration."""
    print("🚀 Setting up Lunch Menu App...")
    
    # Get the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create necessary directories
    directories = [
        'instance',
        'logs',
        'app/templates/errors',
        'app/static/css',
        'app/static/js'
    ]
    
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, mode=0o755)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")
    
    # Create .env file if it doesn't exist
    env_path = os.path.join(base_dir, '.env')
    if not os.path.exists(env_path):
        secret_key = secrets.token_hex(32)
        env_content = f"""# Environment variables for Lunch Menu App
SECRET_KEY={secret_key}
FLASK_ENV=development
DATABASE_URL=sqlite:///{os.path.join(base_dir, 'instance', 'app.db')}
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with secure SECRET_KEY")
    else:
        print("✅ .env file exists")
    
    # Create .gitignore if it doesn't exist
    gitignore_path = os.path.join(base_dir, '.gitignore')
    if not os.path.exists(gitignore_path):
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Flask
instance/
.webassets-cache
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Database
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db

# Test files
htmlcov/
.coverage
.pytest_cache/

# Temporary files
*.tmp
*.bak
erste_campus_*.html
erste_campus_*.json
api_*.json
menu_data.json
page_props.json
react_data.json
selenium_rendered.html
final_rendered_page.html
"""
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore file")
    
    print("\n✅ Setup complete! You can now run: python run.py")


if __name__ == "__main__":
    setup_project()
