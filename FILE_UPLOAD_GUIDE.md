# File Upload Guide

This guide explains how to use the updated college data submission endpoint that now supports file uploads to Supabase storage instead of URLs.

## Overview

The college data submission endpoint has been modified to handle file uploads directly to Supabase storage. Files are uploaded and stored securely, with public URLs generated for access.

## Supported File Types

The following file types are supported:
- **Images**: JPEG, PNG, GIF
- **Documents**: PDF, DOC, DOCX

Maximum file size: 10MB per file

## API Endpoint

**POST** `/api/v1/colleges/submit`

**Content-Type**: `multipart/form-data`

## Required Form Fields

### College Basic Information
- `college_code` (string): Unique college code
- `name` (string): College name
- `short_name` (string, optional): Short name
- `type` (enum): PRIVATE, GOVERNMENT, AIDED
- `university_affiliation` (string, optional): University affiliation
- `year_established` (integer, optional): Year established
- `naac_grade` (string, optional): NAAC grade
- `nba_status` (boolean): NBA status
- `aicte_approved` (boolean): AICTE approval status
- `counselling_type` (enum): UG, PG, BOTH

### Address Information
- `address_line1` (string): Address line 1
- `address_line2` (string, optional): Address line 2
- `city` (string): City
- `district` (string): District
- `state` (string): State (default: Tamil Nadu)
- `pincode` (string): 6-digit pincode

### Contact Information
- `phone` (string, optional): Phone number
- `mobile` (string): 10-digit mobile number
- `email` (string): Email address
- `website` (string, optional): Website URL

### Principal Information
- `principal_name` (string): Principal name
- `principal_designation` (string, optional): Designation
- `principal_phone` (string, optional): Principal phone
- `principal_email` (string): Principal email

### Seat Matrix
- `seat_matrix` (JSON string): Array of seat matrix objects

Example:
```json
[
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
```

### Facilities
- `hostel_available` (boolean): Hostel availability
- `transport_available` (boolean): Transport availability
- `wifi_available` (boolean): WiFi availability
- `lab_facilities` (string, optional): Laboratory facilities
- `placement_cell` (boolean): Placement cell availability

### Bank Details
- `bank_name` (string): Bank name
- `branch` (string, optional): Branch name
- `account_number` (string): Account number (9-18 digits)
- `ifsc_code` (string): IFSC code (11 characters)
- `upi_id` (string, optional): UPI ID

### Document Types
- `document_types` (JSON string): Array of document type names

Example:
```json
[
  "AICTE Approval Certificate",
  "NAAC Certificate",
  "University Affiliation Certificate"
]
```

## File Uploads

### Required Files
- `document_files` (array): Multiple document files
- `document_types` (JSON string): Must match the number of document files

### Optional Files
- `logo_file`: College logo (image file)
- `principal_id_proof_file`: Principal ID proof document
- `cancelled_cheque_file`: Cancelled cheque document

## Example Usage

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/colleges/submit" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "college_code=TEST001" \
  -F "name=Test Engineering College" \
  -F "short_name=TEC" \
  -F "type=PRIVATE" \
  -F "university_affiliation=Anna University" \
  -F "year_established=2020" \
  -F "naac_grade=A" \
  -F "nba_status=true" \
  -F "aicte_approved=true" \
  -F "counselling_type=UG" \
  -F "address_line1=123 Test Street" \
  -F "city=Chennai" \
  -F "district=Chennai" \
  -F "state=Tamil Nadu" \
  -F "pincode=600001" \
  -F "mobile=9876543210" \
  -F "email=test@college.com" \
  -F "principal_name=Dr. Test Principal" \
  -F "principal_email=principal@testcollege.com" \
  -F "seat_matrix=[{\"course_name\":\"Computer Science Engineering\",\"intake_capacity\":60,\"general_seats\":30,\"sc_seats\":9,\"st_seats\":5,\"obc_seats\":16,\"minority_seats\":0}]" \
  -F "hostel_available=true" \
  -F "transport_available=true" \
  -F "wifi_available=true" \
  -F "lab_facilities=Computer labs, Electronics labs" \
  -F "placement_cell=true" \
  -F "bank_name=Test Bank" \
  -F "account_number=1234567890" \
  -F "ifsc_code=TEST0001234" \
  -F "document_types=[\"AICTE Approval Certificate\",\"NAAC Certificate\",\"University Affiliation Certificate\"]" \
  -F "logo_file=@logo.png" \
  -F "principal_id_proof_file=@id_proof.pdf" \
  -F "cancelled_cheque_file=@cheque.pdf" \
  -F "document_files=@aicte_cert.pdf" \
  -F "document_files=@naac_cert.pdf" \
  -F "document_files=@affiliation_cert.pdf"
```

### Using JavaScript/Fetch

```javascript
const formData = new FormData();

// Add form fields
formData.append('college_code', 'TEST001');
formData.append('name', 'Test Engineering College');
formData.append('short_name', 'TEC');
formData.append('type', 'PRIVATE');
formData.append('university_affiliation', 'Anna University');
formData.append('year_established', '2020');
formData.append('naac_grade', 'A');
formData.append('nba_status', 'true');
formData.append('aicte_approved', 'true');
formData.append('counselling_type', 'UG');

// Address
formData.append('address_line1', '123 Test Street');
formData.append('city', 'Chennai');
formData.append('district', 'Chennai');
formData.append('state', 'Tamil Nadu');
formData.append('pincode', '600001');

// Contact
formData.append('mobile', '9876543210');
formData.append('email', 'test@college.com');

// Principal
formData.append('principal_name', 'Dr. Test Principal');
formData.append('principal_email', 'principal@testcollege.com');

// Seat matrix
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

// Facilities
formData.append('hostel_available', 'true');
formData.append('transport_available', 'true');
formData.append('wifi_available', 'true');
formData.append('lab_facilities', 'Computer labs, Electronics labs');
formData.append('placement_cell', 'true');

// Bank details
formData.append('bank_name', 'Test Bank');
formData.append('account_number', '1234567890');
formData.append('ifsc_code', 'TEST0001234');

// Document types
formData.append('document_types', JSON.stringify([
  'AICTE Approval Certificate',
  'NAAC Certificate',
  'University Affiliation Certificate'
]));

// Add files
formData.append('logo_file', logoFile);
formData.append('principal_id_proof_file', idProofFile);
formData.append('cancelled_cheque_file', chequeFile);
formData.append('document_files', document1File);
formData.append('document_files', document2File);
formData.append('document_files', document3File);

// Make request
const response = await fetch('/api/v1/colleges/submit', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: formData
});

const result = await response.json();
console.log(result);
```

## Response Format

### Success Response (200)
```json
{
  "message": "College data submitted successfully and pending verification",
  "college_id": 1,
  "college_code": "TEST001",
  "status": "pending"
}
```

### Error Responses

**400 Bad Request**
```json
{
  "detail": "File type image/gif not allowed. Allowed types: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']"
}
```

**400 Bad Request**
```json
{
  "detail": "File size 15728640 bytes exceeds maximum allowed size of 10485760 bytes"
}
```

**400 Bad Request**
```json
{
  "detail": "Number of document files must match number of document types"
}
```

## File Storage

Files are uploaded to Supabase storage in the following buckets:
- `college-logos`: College logo files
- `principal-documents`: Principal ID proof files
- `college-documents`: College document files
- `bank-documents`: Bank-related documents (cancelled cheques)

Each file gets a unique filename with UUID to prevent conflicts.

## Security Features

- File type validation
- File size limits (10MB max)
- Unique filename generation
- Secure storage in Supabase
- Public URL generation for access

## Testing

You can use the provided test script to verify the functionality:

```bash
python test_file_upload.py
```

Make sure the server is running on `http://localhost:8000` before running the test. 