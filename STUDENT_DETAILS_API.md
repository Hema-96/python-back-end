# Student Details API Endpoint

## Overview

The Student Details API endpoint allows administrators to retrieve comprehensive information about a specific student by their ID. This endpoint follows the same pattern and structure as the existing college details endpoint.

## Endpoint

```
GET /students/{student_id}
```

## Authentication

**Required Role:** Admin (Role 1)

This endpoint requires admin authentication. Include the Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `student_id` | integer | Yes | The user ID of the student to retrieve |

## Response Format

### Success Response (200 OK)

```json
{
  "message": "Student details retrieved successfully",
  "data": {
    "user": {
      "id": 123,
      "email": "student@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "phone": "+1234567890",
      "is_active": true,
      "is_verified": false,
      "last_login": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    "student": {
      "id": 456,
      "user_id": 123,
      "date_of_birth": "2000-01-01T00:00:00Z",
      "gender": "Male",
      "address_line1": "123 Main Street",
      "address_line2": "Apt 4B",
      "city": "Chennai",
      "district": "Chennai",
      "state": "Tamil Nadu",
      "pincode": "600001",
      "parent_name": "Jane Doe",
      "parent_phone": "+1234567891",
      "parent_email": "parent@example.com",
      "caste_category": "General",
      "annual_income": 50000.0,
      "minority_status": false,
      "physically_challenged": false,
      "sports_quota": false,
      "ncc_quota": false,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    "documents": [
      {
        "id": 789,
        "student_id": 456,
        "document_type": "Document",
        "doc_path": "uploads/student-documents/doc123.pdf",
        "file_name": "income_certificate.pdf",
        "doc_url": "https://storage.example.com/signed-url...",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "verification_status": {
      "id": 101,
      "status": "PENDING",
      "remarks": null,
      "verified_by_user_id": null,
      "verified_at": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

### Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

#### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

#### 404 Not Found
```json
{
  "detail": "Student user not found"
}
```

or

```json
{
  "detail": "Student profile not found"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Data Structure

### User Information
- **id**: User's unique identifier
- **email**: User's email address
- **first_name**: User's first name
- **last_name**: User's last name
- **phone**: User's phone number
- **is_active**: Whether the user account is active
- **is_verified**: Whether the user's email is verified
- **last_login**: Timestamp of last login
- **created_at**: Account creation timestamp
- **updated_at**: Last update timestamp

### Student Profile
- **id**: Student record unique identifier
- **user_id**: Reference to user table
- **date_of_birth**: Student's date of birth
- **gender**: Student's gender (Male, Female, Other)
- **address_line1**: Primary address line
- **address_line2**: Secondary address line (optional)
- **city**: City name
- **district**: District name
- **state**: State name (defaults to "Tamil Nadu")
- **pincode**: Postal code
- **parent_name**: Parent/Guardian name
- **parent_phone**: Parent/Guardian phone number
- **parent_email**: Parent/Guardian email (optional)
- **caste_category**: Caste category (General, SC, ST, OBC, MBC, Other)
- **annual_income**: Annual family income (optional)
- **minority_status**: Whether student belongs to minority community
- **physically_challenged**: Whether student is physically challenged
- **sports_quota**: Whether student is eligible for sports quota
- **ncc_quota**: Whether student is eligible for NCC quota

### Documents
Array of student documents with:
- **id**: Document unique identifier
- **student_id**: Reference to student record
- **document_type**: Type of document
- **doc_path**: File path in storage
- **file_name**: Original file name
- **doc_url**: Signed URL for file access (expires in 1 hour)
- **created_at**: Document creation timestamp
- **updated_at**: Last update timestamp

### Verification Status
- **id**: Verification record unique identifier
- **status**: Current status (PENDING, APPROVED, REJECTED)
- **remarks**: Admin remarks (optional)
- **verified_by_user_id**: Admin who verified (optional)
- **verified_at**: Verification timestamp (optional)
- **created_at**: Record creation timestamp
- **updated_at**: Last update timestamp

## Usage Examples

### cURL Example

```bash
# Login to get token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123" | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Get student details
curl -X GET "http://localhost:8000/students/123" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Python Example

```python
import requests

# Login
login_response = requests.post("http://localhost:8000/auth/login", data={
    "username": "admin@example.com",
    "password": "admin123"
})
token = login_response.json()["access_token"]

# Get student details
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/students/123", headers=headers)
student_data = response.json()
```

### JavaScript Example

```javascript
// Login
const loginResponse = await fetch("http://localhost:8000/auth/login", {
    method: "POST",
    headers: {"Content-Type": "application/x-www-form-urlencoded"},
    body: "username=admin@example.com&password=admin123"
});
const { access_token } = await loginResponse.json();

// Get student details
const response = await fetch("http://localhost:8000/students/123", {
    headers: {"Authorization": `Bearer ${access_token}`}
});
const studentData = await response.json();
```

## Security Features

1. **Admin-only access**: Only users with admin role (Role 1) can access this endpoint
2. **Authentication required**: Valid JWT token must be provided
3. **Signed URLs**: Document URLs are signed and expire after 1 hour
4. **Input validation**: Student ID is validated as an integer
5. **Error handling**: Comprehensive error handling with appropriate HTTP status codes

## Rate Limiting

This endpoint follows the same rate limiting rules as other API endpoints in the system.

## Notes

- The `student_id` parameter is actually the `user_id` from the users table
- Documents are returned with signed URLs that expire after 1 hour
- If no documents exist, the `documents` field will be an empty array
- If no verification status exists, the `verification_status` field will be null
- All timestamps are in ISO 8601 format (UTC)

## Related Endpoints

- `GET /students/all` - Get all students (Admin only)
- `GET /students/pending` - Get pending students (Admin only)
- `GET /students/approved` - Get approved students (Public)
- `GET /students/{student_id}/documents` - Get student documents
- `POST /students/{user_id}/verify` - Verify/reject student (Admin only)
