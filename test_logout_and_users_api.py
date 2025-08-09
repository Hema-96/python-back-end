#!/usr/bin/env python3
"""
Test script for the new logout API and admin users list API
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_login_and_logout():
    """Test login and logout functionality"""
    print("=== Testing Login and Logout API ===")
    
    # Test login
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    print(f"1. Logging in with: {login_data['email']}")
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    
    if response.status_code == 200:
        login_result = response.json()
        access_token = login_result.get("access_token")
        print(f"✅ Login successful! Token received: {access_token[:20]}...")
        
        # Test using the token
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        
        if me_response.status_code == 200:
            user_info = me_response.json()
            print(f"✅ Token is valid! User: {user_info.get('email')}")
        else:
            print(f"❌ Token validation failed: {me_response.status_code}")
            return
        
        # Test logout
        print("2. Testing logout...")
        logout_response = requests.post(f"{API_BASE}/auth/logout", headers=headers)
        
        if logout_response.status_code == 200:
            logout_result = logout_response.json()
            print(f"✅ Logout successful! {logout_result}")
        else:
            print(f"❌ Logout failed: {logout_response.status_code}")
            return
        
        # Test that token is now invalid
        print("3. Testing token invalidation...")
        invalid_me_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        
        if invalid_me_response.status_code == 401:
            print("✅ Token successfully invalidated!")
        else:
            print(f"❌ Token still valid after logout: {invalid_me_response.status_code}")
    
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")

def test_admin_users_list():
    """Test admin users list API"""
    print("\n=== Testing Admin Users List API ===")
    
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
        
        # Test admin users list
        headers = {"Authorization": f"Bearer {access_token}"}
        print("2. Fetching all users...")
        users_response = requests.get(f"{API_BASE}/users/all?format=dashboard", headers=headers)
        
        if users_response.status_code == 200:
            users_result = users_response.json()
            users = users_result.get("data", [])
            print(f"✅ Successfully retrieved {len(users)} users!")
            
            print("\n📋 Users List:")
            print("-" * 80)
            for user in users:
                print(f"ID: {user.get('id')}")
                print(f"Name: {user.get('name')}")
                print(f"Email: {user.get('email')}")
                print(f"Role: {user.get('role')}")
                print(f"Status: {user.get('status')}")
                print(f"Last Login: {user.get('lastLogin')}")
                print(f"Registration: {user.get('registrationDate')}")
                print(f"Phone: {user.get('phone')}")
                if user.get('institution'):
                    print(f"Institution: {user.get('institution')}")
                print("-" * 40)
        else:
            print(f"❌ Failed to get users: {users_response.status_code}")
            print(f"Response: {users_response.text}")
    
    else:
        print(f"❌ Admin login failed: {response.status_code}")
        print(f"Response: {response.text}")

def test_non_admin_access():
    """Test that non-admin users cannot access admin endpoints"""
    print("\n=== Testing Non-Admin Access Control ===")
    
    # Try to access admin endpoint without authentication
    print("1. Testing access without authentication...")
    response = requests.get(f"{API_BASE}/users/all")
    
    if response.status_code == 401:
        print("✅ Properly blocked unauthenticated access!")
    else:
        print(f"❌ Should have blocked unauthenticated access: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Testing Logout and Admin Users APIs")
    print("=" * 50)
    
    try:
        test_login_and_logout()
        test_admin_users_list()
        test_non_admin_access()
        
        print("\n✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error! Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test error: {e}")
