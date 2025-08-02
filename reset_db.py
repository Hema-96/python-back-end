#!/usr/bin/env python3
"""
Script to reset the database manually
Use this when you want to clear all data and start fresh
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import reset_database

def main():
    """Reset the database"""
    print("⚠️  WARNING: This will delete ALL data in the database!")
    print("This action cannot be undone.")
    
    response = input("Are you sure you want to reset the database? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        try:
            print("🔄 Resetting database...")
            reset_database()
            print("✅ Database reset completed successfully!")
        except Exception as e:
            print(f"❌ Error resetting database: {e}")
            sys.exit(1)
    else:
        print("❌ Database reset cancelled.")

if __name__ == "__main__":
    main() 