#!/usr/bin/env python3
"""
Test script for file upload functionality
"""

import requests
import json
import os
from io import BytesIO

# Test configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

def test_file_upload():
    """Test the file upload functionality"""
    
    # First, let's create a test file
    test_file_content = b"This is a test document content"
    test_file = BytesIO(test_file_content)
    
    # Prepare form data
    form_data = {
        # College basic info
        'college_code': 'TEST001',
        'name': 'Test Engineering College',
        'short_name': 'TEC',
        'type': 'PRIVATE',
        'university_affiliation': 'Anna University',
        'year_established': 2020,
        'naac_grade': 'A',
        'nba_status': True,
        'aicte_approved': True,
        'counselling_type': 'UG',
        
        # Address
        'address_line1': '123 Test Street',
        'address_line2': 'Test Area',
        'city': 'Chennai',
        'district': 'Chennai',
        'state': 'Tamil Nadu',
        'pincode': '600001',
        
        # Contact
        'phone': '0441234567',
        'mobile': '9876543210',
        'email': 'test@college.com',
        'website': 'https://testcollege.com',
        
        # Principal info
        'principal_name': 'Dr. Test Principal',
        'principal_designation': 'Principal',
        'principal_phone': '0441234568',
        'principal_email': 'principal@testcollege.com',
        
        # Seat matrix
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
        
        # Facilities
        'hostel_available': True,
        'transport_available': True,
        'wifi_available': True,
        'lab_facilities': 'Computer labs, Electronics labs',
        'placement_cell': True,
        
        # Bank details
        'bank_name': 'Test Bank',
        'branch': 'Chennai Main',
        'account_number': '1234567890',
        'ifsc_code': 'TEST0001234',
        'upi_id': 'testcollege@testbank',
        
        # Document types
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
    
    try:
        # Make the request
        response = requests.post(
            f"{API_URL}/colleges/submit",
            data=form_data,
            files=files
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ File upload test passed!")
        else:
            print("❌ File upload test failed!")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    print("Testing file upload functionality...")
    test_file_upload() 