# test_db.py
import os
import sqlite3

def test_database_connection():
    """Test if we can create and connect to the database."""
    print("Testing database connection...")
    
    # Get paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    db_path = os.path.join(instance_dir, 'app.db')
    
    print(f"Base directory: {base_dir}")
    print(f"Instance directory: {instance_dir}")
    print(f"Database path: {db_path}")
    
    # Create instance directory if it doesn't exist
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
        print("✅ Created instance directory")
    
    # Test SQLite connection
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()
        print("✅ Successfully connected to SQLite database")
        
        # Check file permissions
        import stat
        file_stat = os.stat(db_path)
        print(f"Database file permissions: {oct(file_stat.st_mode)[-3:]}")
        
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")


if __name__ == "__main__":
    test_database_connection()
