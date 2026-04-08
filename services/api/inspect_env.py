import os
import sys
import main
print(f"Main file: {main.__file__}")
print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")
try:
    from core.routers import billing
    print("Billing imported successfully")
except ImportError as e:
    print(f"Billing import failed: {e}")
