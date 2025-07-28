# debug_imports.py
import os
import sys

print("Current directory:", os.getcwd())
print("\nPython path:")
for p in sys.path[:5]:
    print(f"  - {p}")

print("\nTrying imports:")
try:
    from config import config
    print("✅ Successfully imported config")
    print(f"   Config keys: {list(config.keys())}")
except ImportError as e:
    print(f"❌ Failed to import config: {e}")

try:
    from app import create_app
    print("✅ Successfully imported create_app")
except ImportError as e:
    print(f"❌ Failed to import create_app: {e}")

try:
    from app.models import Restaurant, MenuItem
    print("✅ Successfully imported models")
except ImportError as e:
    print(f"❌ Failed to import models: {e}")
