#!/usr/bin/env python3
"""
Test script to verify Supabase file upload functionality
"""

import requests
import json
from io import BytesIO

def test_supabase_upload():
    """Test Supabase file upload functionality"""
    
    # Test configuration
    BASE_URL = "http://127.0.0.1:8000"
    API_URL = f"{BASE_URL}/api/v1"
    
    # Your token here
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZW1haWwiOiJjb2xsZWdlMkBhZ2lsZWN5YmVyLmNvbSIsInJvbGUiOjIsImV4cCI6MTc1NDE5MDg2MywidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1NDE4OTA2M30.LNNAWM3gZmJ6eE6QdIBUrUFa5cYMk3yFNfwWe4OvXyo"
    
    # Create test file content
    test_file_content = b"This is a test document content for Supabase upload"
    test_file = BytesIO(test_file_content)
    
    # Prepare minimal form data
    form_data = {
        'college_code': 'TEST001',
        'name': 'Test College',
        'type': 'Private',
        'counselling_type': 'UG',
        'address_line1': '123 Test Street',
        'city': 'Chennai',
        'district': 'Chennai',
        'state': 'Tamil Nadu',
        'pincode': '600001',
        'mobile': '9876543210',
        'email': 'test@college.com',
        'principal_name': 'Dr. Test Principal',
        'principal_email': 'principal@testcollege.com',
        'seat_matrix': json.dumps([
            {
                'course_name': 'Computer Science Engineering',
                'intake_capacity': 60,
                'general_seats': 30,
                'sc_seats': 9,
                'st_seats': 5,
                'obc_seats': 16,
                'minority_seats': 0
            }
        ]),
        'bank_name': 'Test Bank',
        'account_number': '1234567890',
        'ifsc_code': 'TEST0001234',
        'document_types': json.dumps([
            'AICTE Approval Certificate'
        ])
    }
    
    # Prepare minimal files
    files = {
        'document_files': [
            ('test_document.pdf', test_file, 'application/pdf')
        ]
    }
    
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'accept': 'application/json'
    }
    
    try:
        print("🔄 Testing Supabase file upload...")
        print(f"📡 URL: {API_URL}/colleges/submit")
        print(f"🔑 Token: {TOKEN[:20]}...")
        
        response = requests.post(
            f"{API_URL}/colleges/submit",
            data=form_data,
            files=files,
            headers=headers
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"📋 Response JSON: {json.dumps(response_json, indent=2)}")
            
            if response.status_code == 200:
                print("✅ Supabase upload test passed!")
                print("🎉 Files are now stored in Supabase storage!")
            else:
                print("❌ Supabase upload test failed!")
                
        except json.JSONDecodeError:
            print(f"📄 Response Text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_supabase_upload() 