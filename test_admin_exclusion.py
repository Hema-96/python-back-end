#!/usr/bin/env python3
"""
Test script to verify admin users are excluded from the users list API
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_admin_exclusion():
    """Test that admin users are excluded from the users list"""
    print("=== Testing Admin User Exclusion ===")
    
    # First login as admin
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    print("1. Logging in as admin...")
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    
    if response.status_code == 200:
        login_result = response.json()
        access_token = login_result.get("access_token")
        print(f"✅ Admin login successful!")
        
        # Test users list with dashboard format
        headers = {"Authorization": f"Bearer {access_token}"}
        print("2. Fetching users (admin users should be excluded)...")
        users_response = requests.get(f"{API_BASE}/users/all?format=dashboard", headers=headers)
        
        if users_response.status_code == 200:
            users_result = users_response.json()
            users = users_result.get("data", [])
            print(f"✅ Successfully retrieved {len(users)} users!")
            
            # Check if any admin users are in the results
            admin_users = [user for user in users if user.get('role') == 'admin']
            
            if len(admin_users) == 0:
                print("✅ Admin users correctly excluded from results!")
            else:
                print(f"❌ Found {len(admin_users)} admin users in results (should be 0)")
                for admin in admin_users:
                    print(f"   - Admin: {admin.get('name')} ({admin.get('email')})")
            
            # Show what user types are included
            user_types = {}
            for user in users:
                role = user.get('role')
                user_types[role] = user_types.get(role, 0) + 1
            
            print(f"\n📊 User types in results:")
            for role, count in user_types.items():
                print(f"   - {role}: {count}")
            
            # Show sample users
            if users:
                print(f"\n📋 Sample users (first 3):")
                for i, user in enumerate(users[:3]):
                    print(f"   {i+1}. {user.get('name')} ({user.get('email')}) - {user.get('role')} - {user.get('status')}")
            
        else:
            print(f"❌ Failed to get users: {users_response.status_code}")
            print(f"Response: {users_response.text}")
    
    else:
        print(f"❌ Admin login failed: {response.status_code}")
        print(f"Response: {response.text}")

def test_standard_format():
    """Test standard format also excludes admin users"""
    print("\n=== Testing Standard Format ===")
    
    # Login as admin
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    
    if response.status_code == 200:
        login_result = response.json()
        access_token = login_result.get("access_token")
        
        # Test standard format
        headers = {"Authorization": f"Bearer {access_token}"}
        users_response = requests.get(f"{API_BASE}/users/all", headers=headers)
        
        if users_response.status_code == 200:
            users = users_response.json()
            print(f"✅ Standard format: Retrieved {len(users)} users")
            
            # Check for admin users
            admin_users = [user for user in users if user.get('role') == 1]  # UserRole.ADMIN = 1
            
            if len(admin_users) == 0:
                print("✅ Admin users correctly excluded from standard format!")
            else:
                print(f"❌ Found {len(admin_users)} admin users in standard format")
        else:
            print(f"❌ Standard format failed: {users_response.status_code}")

if __name__ == "__main__":
    print("🚀 Testing Admin User Exclusion")
    print("=" * 50)
    
    try:
        test_admin_exclusion()
        test_standard_format()
        
        print("\n✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error! Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test error: {e}")
