# init_db.py
import os
import sys

# Add the project to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Create necessary directories
base_dir = os.path.dirname(os.path.abspath(__file__))
instance_dir = os.path.join(base_dir, 'instance')
logs_dir = os.path.join(base_dir, 'logs')

# Create directories with proper permissions
for directory in [instance_dir, logs_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory, mode=0o755, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    else:
        print(f"✅ Directory exists: {directory}")

# Create a simple .env file if it doesn't exist
env_file = os.path.join(base_dir, '.env')
if not os.path.exists(env_file):
    with open(env_file, 'w') as f:
        f.write("""SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
DATABASE_URL=sqlite:///instance/app.db
""")
    print(f"✅ Created .env file: {env_file}")
else:
    print(f"✅ .env file exists: {env_file}")

print("\n✅ Initialization complete!")
