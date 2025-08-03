#!/usr/bin/env python3
"""
Debug script to test the college submission API
"""

import requests
import json
from io import BytesIO

def test_college_submission():
    """Test the college submission API with proper error handling"""
    
    # Test configuration
    BASE_URL = "http://127.0.0.1:8000"
    API_URL = f"{BASE_URL}/api/v1"
    
    # Your token here
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZW1haWwiOiJjb2xsZWdlMkBhZ2lsZWN5YmVyLmNvbSIsInJvbGUiOjIsImV4cCI6MTc1NDE5MDg2MywidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1NDE4OTA2M30.LNNAWM3gZmJ6eE6QdIBUrUFa5cYMk3yFNfwWe4OvXyo"
    
    # Create test file content
    test_file_content = b"This is a test document content"
    test_file = BytesIO(test_file_content)
    
    # Prepare form data with correct JSON format
    form_data = {
        'college_code': 'TEST001',
        'name': 'Test Engineering College',
        'short_name': 'TEC',
        'type': 'Private',  # Correct enum value
        'university_affiliation': 'Anna University',
        'year_established': 2020,
        'naac_grade': 'A',
        'nba_status': False,
        'aicte_approved': False,
        'counselling_type': 'UG',  # Correct enum value
        'address_line1': '123 Test Street',
        'address_line2': 'Test Area',
        'city': 'Chennai',
        'district': 'Chennai',
        'state': 'Tamil Nadu',
        'pincode': '600001',
        'phone': '0441234567',
        'mobile': '9876543210',
        'email': 'test@college.com',
        'website': 'https://testcollege.com',
        'principal_name': 'Dr. Test Principal',
        'principal_designation': 'Principal',
        'principal_phone': '0441234568',
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
        'hostel_available': False,
        'transport_available': False,
        'wifi_available': False,
        'lab_facilities': 'Computer labs, Electronics labs',
        'placement_cell': False,
        'bank_name': 'Test Bank',
        'branch': 'Chennai Main',
        'account_number': '1234567890',
        'ifsc_code': 'TEST0001234',
        'upi_id': 'testcollege@testbank',
        'document_types': json.dumps([
            'AICTE Approval Certificate',
            'NAAC Certificate',
            'University Affiliation Certificate'
        ])
    }
    
    # Prepare files
    files = {
        'logo_file': ('logo.png', test_file, 'image/png'),
        'principal_id_proof_file': ('id_proof.pdf', test_file, 'application/pdf'),
        'cancelled_cheque_file': ('cheque.pdf', test_file, 'application/pdf'),
        'document_files': [
            ('aicte_cert.pdf', test_file, 'application/pdf'),
            ('naac_cert.pdf', test_file, 'application/pdf'),
            ('affiliation_cert.pdf', test_file, 'application/pdf')
        ]
    }
    
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'accept': 'application/json'
    }
    
    try:
        print("🔄 Testing college submission API...")
        print(f"📡 URL: {API_URL}/colleges/submit")
        print(f"🔑 Token: {TOKEN[:20]}...")
        
        response = requests.post(
            f"{API_URL}/colleges/submit",
            data=form_data,
            files=files,
            headers=headers
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"📋 Response JSON: {json.dumps(response_json, indent=2)}")
        except json.JSONDecodeError:
            print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ API test passed!")
        else:
            print("❌ API test failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_college_submission() 