# File Upload Guide

This guide explains how to use the file upload functionality in the Tamil Nadu Engineering College Counselling API.

## 🚀 Overview

The API supports file uploads for college documents, logos, and other required files. All files are stored securely in **Supabase Storage** with public URLs for easy access.

## 📁 Supported File Types

### Allowed File Types
- **Images**: `image/jpeg`, `image/png`, `image/gif`
- **Documents**: `application/pdf`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- **Maximum File Size**: 10MB per file

### File Categories
- **College Logos**: College branding and identification
- **Principal Documents**: Principal ID proofs and certificates
- **College Documents**: AICTE approvals, NAAC certificates, etc.
- **Bank Documents**: Cancelled cheques and bank statements

## 🔧 API Endpoint

### Submit College Data with Files
```http
POST /api/v1/colleges/submit
Content-Type: multipart/form-data
Authorization: Bearer <your_jwt_token>
```

## 📋 Form Fields

### Required College Information
```bash
# Basic Information
college_code=string
name=string
type=Private|Government|Aided|Self Financing
counselling_type=UG|PG|Diploma

# Address Information
address_line1=string
address_line2=string (optional)
city=string
district=string
state=string
pincode=string

# Contact Information
mobile=string
email=string
phone=string (optional)
website=string (optional)

# Principal Information
principal_name=string
principal_email=string
principal_phone=string
principal_designation=string

# College Details
year_established=number
short_name=string
college_code=string
university_affiliation=string
aicte_approved=boolean
nba_status=boolean
naac_grade=string

# Facilities
lab_facilities=string
transport_available=boolean
hostel_available=boolean
wifi_available=boolean
placement_cell=boolean

# Bank Details
bank_name=string
account_number=string
ifsc_code=string
upi_id=string

# Seat Matrix (JSON string)
seat_matrix=[
  {
    "course_name": "Computer Science Engineering",
    "intake_capacity": 60,
    "general_seats": 30,
    "sc_seats": 9,
    "st_seats": 5,
    "obc_seats": 16,
    "minority_seats": 0
  }
]

# Document Types (JSON string)
document_types=["AICTE Approval Certificate", "NAAC Certificate"]
```

### File Upload Fields
```bash
# File uploads (all optional)
logo_file=@file.pdf
principal_id_proof_file=@file.pdf
doc_file=@file.pdf
cancelled_cheque_file=@file.pdf
document_files=@file1.pdf
document_files=@file2.pdf
```

## 🧪 Testing Examples

### Using cURL
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/colleges/submit' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: multipart/form-data' \
  -F 'college_code=TEST001' \
  -F 'name=Test College' \
  -F 'type=Private' \
  -F 'counselling_type=UG' \
  -F 'address_line1=123 Test Street' \
  -F 'city=Chennai' \
  -F 'district=Chennai' \
  -F 'state=Tamil Nadu' \
  -F 'pincode=600001' \
  -F 'mobile=9876543210' \
  -F 'email=test@college.com' \
  -F 'principal_name=Dr. Test Principal' \
  -F 'principal_email=principal@testcollege.com' \
  -F 'seat_matrix=[{"course_name":"Computer Science Engineering","intake_capacity":60,"general_seats":30,"sc_seats":9,"st_seats":5,"obc_seats":16,"minority_seats":0}]' \
  -F 'bank_name=Test Bank' \
  -F 'account_number=1234567890' \
  -F 'ifsc_code=TEST0001234' \
  -F 'document_types=["AICTE Approval Certificate"]' \
  -F 'document_files=@test_document.pdf'
```

### Using Python Requests
```python
import requests
import json

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api/v1"
TOKEN = "your_jwt_token_here"

# Prepare form data
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

# Prepare files
files = {
    'document_files': [
        ('test_document.pdf', open('test_document.pdf', 'rb'), 'application/pdf')
    ]
}

# Headers
headers = {
    'Authorization': f'Bearer {TOKEN}',
    'accept': 'application/json'
}

# Make request
response = requests.post(
    f"{API_URL}/colleges/submit",
    data=form_data,
    files=files,
    headers=headers
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
```

### Using JavaScript/Fetch
```javascript
const formData = new FormData();

// Add form fields
formData.append('college_code', 'TEST001');
formData.append('name', 'Test College');
formData.append('type', 'Private');
formData.append('counselling_type', 'UG');
formData.append('address_line1', '123 Test Street');
formData.append('city', 'Chennai');
formData.append('district', 'Chennai');
formData.append('state', 'Tamil Nadu');
formData.append('pincode', '600001');
formData.append('mobile', '9876543210');
formData.append('email', 'test@college.com');
formData.append('principal_name', 'Dr. Test Principal');
formData.append('principal_email', 'principal@testcollege.com');

// Add JSON fields
formData.append('seat_matrix', JSON.stringify([
    {
        course_name: 'Computer Science Engineering',
        intake_capacity: 60,
        general_seats: 30,
        sc_seats: 9,
        st_seats: 5,
        obc_seats: 16,
        minority_seats: 0
    }
]));

formData.append('bank_name', 'Test Bank');
formData.append('account_number', '1234567890');
formData.append('ifsc_code', 'TEST0001234');
formData.append('document_types', JSON.stringify([
    'AICTE Approval Certificate'
]));

// Add files
const fileInput = document.getElementById('document-files');
for (let file of fileInput.files) {
    formData.append('document_files', file);
}

// Make request
fetch('http://127.0.0.1:8000/api/v1/colleges/submit', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_JWT_TOKEN'
    },
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Success:', data);
})
.catch(error => {
    console.error('Error:', error);
});
```

## 📊 Response Format

### Success Response
```json
{
  "message": "College data submitted successfully",
  "college_id": 1,
  "verification_status": "pending",
  "uploaded_files": [
    {
      "file_name": "test_document.pdf",
      "file_url": "https://poptklbkuamytrzcgeiy.supabase.co/storage/v1/object/public/uploads/uuid_filename.pdf",
      "file_size": 1024,
      "content_type": "application/pdf",
      "storage_type": "supabase"
    }
  ]
}
```

### Error Response
```json
{
  "detail": "File type application/txt not allowed. Allowed types: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']"
}
```

## 🔍 File Storage Details

### Supabase Storage
- **Bucket**: `uploads`
- **File Naming**: `{uuid}_{original_filename}`
- **Public URLs**: Automatically generated
- **Security**: Files are publicly accessible via URLs

### File Organization
Files are stored in the Supabase storage bucket with unique filenames to prevent conflicts. The original filename is preserved in the response for reference.

## 🚨 Common Issues

### 1. File Type Not Allowed
**Error**: `File type application/txt not allowed`
**Solution**: Use only supported file types (PDF, DOC, DOCX, JPEG, PNG, GIF)

### 2. File Too Large
**Error**: `File size 15000000 bytes exceeds maximum allowed size of 10485760 bytes`
**Solution**: Compress files or use smaller files (max 10MB)

### 3. Invalid JSON Format
**Error**: `Invalid JSON format for seat_matrix`
**Solution**: Ensure JSON strings are properly formatted arrays of objects

### 4. Authentication Required
**Error**: `Not authenticated`
**Solution**: Include valid JWT token in Authorization header

### 5. Supabase Upload Error
**Error**: `Supabase upload error: ...`
**Solution**: Check Supabase configuration and bucket permissions

## 🧪 Testing Tools

### Test Script
Run the provided test script to verify file upload functionality:
```bash
python test_supabase_upload.py
```

### Manual Testing
1. Start the server: `uvicorn app.main:app --reload`
2. Use the cURL example above
3. Check the response for file URLs
4. Verify files are accessible via the returned URLs

## 📝 Notes

- All files are validated for type and size before upload
- Files are stored with unique UUIDs to prevent conflicts
- Public URLs are generated automatically for file access
- The API supports multiple file uploads for document_files
- File metadata is stored in the database for reference 