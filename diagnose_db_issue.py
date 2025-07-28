# diagnose_db_issue.py
import os
import sys
import sqlite3
from pathlib import Path

def diagnose_database_issue():
    """Diagnose database connection issues."""
    print("🔍 Diagnosing Database Connection Issue")
    print("=" * 60)
    
    # 1. Check current working directory
    cwd = os.getcwd()
    print(f"\n1. Current working directory: {cwd}")
    
    # 2. Check script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"2. Script directory: {script_dir}")
    
    # 3. Check if instance directory exists
    instance_path = os.path.join(script_dir, 'instance')
    print(f"\n3. Instance directory path: {instance_path}")
    print(f"   Exists: {os.path.exists(instance_path)}")
    
    if os.path.exists(instance_path):
        # Check permissions
        try:
            # Try to create a test file
            test_file = os.path.join(instance_path, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print("   ✅ Write permissions: OK")
        except Exception as e:
            print(f"   ❌ Write permissions: FAILED - {e}")
    else:
        # Create the directory
        try:
            os.makedirs(instance_path, exist_ok=True)
            print("   ✅ Created instance directory")
        except Exception as e:
            print(f"   ❌ Failed to create directory: {e}")
    
    # 4. Test SQLite connection with different paths
    print("\n4. Testing SQLite connections:")
    
    # Test different database paths
    db_paths = [
        os.path.join(instance_path, 'app.db'),
        os.path.join(script_dir, 'instance', 'app.db'),
        os.path.join(script_dir, 'app.db'),
        'instance/app.db',
        'app.db'
    ]
    
    for db_path in db_paths:
        print(f"\n   Testing: {db_path}")
        try:
            # Try to connect
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            conn.close()
            print(f"   ✅ Success! SQLite version: {version}")
            print(f"   Absolute path: {os.path.abspath(db_path)}")
            break
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # 5. Check Python path
    print("\n5. Python path:")
    for path in sys.path[:5]:
        print(f"   - {path}")
    
    # 6. Check Flask-SQLAlchemy database URI format
    print("\n6. Testing database URI formats:")
    
    # Get absolute path
    abs_db_path = os.path.join(script_dir, 'instance', 'app.db')
    
    uris = [
        f"sqlite:///{abs_db_path}",
        f"sqlite:///instance/app.db",
        f"sqlite:///./instance/app.db",
        f"sqlite:///{os.path.join('instance', 'app.db')}",
    ]
    
    for uri in uris:
        print(f"\n   URI: {uri}")
        # Extract path from URI
        if uri.startswith('sqlite:///'):
            path = uri[10:]  # Remove 'sqlite:///'
            print(f"   Path: {path}")
            print(f"   Exists: {os.path.exists(path)}")


if __name__ == "__main__":
    diagnose_database_issue()
