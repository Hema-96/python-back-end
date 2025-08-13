# Tamil Nadu Engineering College Counselling API Documentation

## Overview
Comprehensive API for Tamil Nadu Engineering College Counselling system with authentication, college/student management, access control, and stage-based flow control.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Include JWT Bearer token in Authorization header:
```
Authorization: Bearer <your_access_token>
```

## API Endpoints Summary

### 🔐 Authentication (`/auth`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Register new user |
| POST | `/auth/login` | No | User login |
| POST | `/auth/refresh` | No | Refresh access token |
| GET | `/auth/me` | Yes | Get current user info |
| POST | `/auth/logout` | Yes | Logout user |
| POST | `/auth/send-email-otp` | No | Send email OTP |
| POST | `/auth/verify-email-otp` | No | Verify email OTP |
| POST | `/auth/password-change` | Yes | Change password |
| POST | `/auth/password-reset` | No | Request password reset |
| POST | `/auth/set-new-password` | No | Set new password |

### 👥 Users (`/users`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/users/admin/profile` | Admin | Create admin profile |
| POST | `/users/college/profile` | College | Create college profile |
| POST | `/users/student/profile` | Student | Create student profile |
| GET | `/users/{role}/profile` | Role | Get profile |
| GET | `/users/all` | Admin | Get all users |
| GET | `/users/colleges` | Admin | Get all colleges |
| PUT | `/users/college/{id}/approve` | Admin | Approve college |
| PUT | `/users/profile` | Yes | Update profile |
| DELETE | `/users/{id}` | Admin | Delete user |

### 🏫 Colleges (`/colleges`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/colleges/submit` | College | Submit college data |
| GET | `/colleges/my-college` | College | Get my college |
| GET | `/colleges/all` | Admin | Get all colleges |
| GET | `/colleges/{id}` | Admin | Get college details |
| POST | `/colleges/{id}/verify` | Admin | Verify college |
| GET | `/colleges/pending` | Admin | Get pending colleges |
| GET | `/colleges/approved` | No | Get approved colleges |
| GET | `/colleges/{id}/documents` | Admin/Owner | Get college documents |

### 👨‍🎓 Students (`/students`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/students/submit` | Student | Submit student data |
| GET | `/students/my-profile` | Student | Get my profile |
| GET | `/students/all` | Admin | Get all students |
| GET | `/students/pending` | Admin | Get pending students |
| GET | `/students/approved` | No | Get approved students |
| POST | `/students/{id}/verify` | Admin | Verify student |
| GET | `/students/{id}/documents` | Admin/Owner | Get student documents |
| GET | `/students/{id}` | Admin | Get student details |

### 🔧 Admin (`/admin`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/admin/dashboard-tiles` | Admin | Get dashboard stats |

### 🔐 Access Control (`/access-control`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/access-control/permissions` | System Admin | Create permission |
| GET | `/access-control/permissions` | System Read | Get permissions |
| GET | `/access-control/permissions/{id}` | System Read | Get permission |
| PUT | `/access-control/permissions/{id}` | System Admin | Update permission |
| POST | `/access-control/roles` | System Admin | Create role |
| GET | `/access-control/roles` | System Read | Get roles |
| GET | `/access-control/roles/{id}` | System Read | Get role |
| PUT | `/access-control/roles/{id}` | System Admin | Update role |
| POST | `/access-control/roles/{id}/permissions` | System Admin | Assign permission to role |
| DELETE | `/access-control/roles/{id}/permissions/{perm_id}` | System Admin | Remove permission from role |
| POST | `/access-control/users/{id}/roles` | User Admin | Assign role to user |
| DELETE | `/access-control/users/{id}/roles/{role_id}` | User Admin | Remove role from user |
| POST | `/access-control/users/bulk-assign-role` | User Admin | Bulk assign role |
| POST | `/access-control/roles/bulk-assign-permission` | System Admin | Bulk assign permission |
| POST | `/access-control/check-permission` | System Read | Check permission |
| GET | `/access-control/users/{id}/permissions` | System Read | Get user permissions |
| POST | `/access-control/initialize` | System Admin | Initialize system |
| GET | `/access-control/health` | System Read | Health check |

### 🎯 Stages (`/stages`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/stages/` | Admin | Create stage |
| GET | `/stages/` | Admin | Get all stages |
| GET | `/stages/current` | No | Get current stage |
| PUT | `/stages/{id}` | Admin | Update stage |
| POST | `/stages/{id}/activate` | Admin | Activate stage |
| POST | `/stages/{id}/deactivate` | Admin | Deactivate stage |
| POST | `/stages/initialize` | Admin | Initialize default stages |
| GET | `/stages/check-registration/{role}` | No | Check registration allowed |

## Request/Response Examples

### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "9876543210",
  "role": 2
}
```

### Login User
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### Submit College Data (Multipart)
```http
POST /api/v1/colleges/submit
Content-Type: multipart/form-data

college_code: ABC001
name: ABC Engineering College
type: Private
address_line1: 123 Main Street
city: Chennai
district: Chennai
mobile: 9876543210
email: college@example.com
principal_name: Principal Name
principal_email: principal@example.com
seat_matrix: [{"course_name":"CSE","intake_capacity":60,"general_seats":30,"sc_seats":10,"st_seats":5,"obc_seats":10,"minority_seats":5}]
bank_name: State Bank
account_number: 1234567890
ifsc_code: SBIN0001234
logo_file: [file]
document_files: [files]
```

### Submit Student Data (Multipart)
```http
POST /api/v1/students/submit
Content-Type: multipart/form-data

date_of_birth: 2000-01-01
gender: Male
address_line1: 456 Student Street
city: Chennai
district: Chennai
parent_name: Parent Name
parent_phone: 9876543210
caste_category: General
document_files: [files]
```

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message description"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid data
- `401 Unauthorized`: Auth required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## File Upload
- **Supported**: JPG, JPEG, PNG, GIF, PDF, DOC, DOCX
- **Max Size**: 10MB per file
- **Endpoints**: College/Student submission endpoints
- **Response**: Signed URLs for file access

## Stage-Based Access Control
- **Stage 1**: College Registration
- **Stage 2**: Student Registration  
- **Stage 3**: Application Processing
- **Stage 4**: Results and Allotment
- **Completed**: System Completed

## Pagination
Most list endpoints support:
- `skip`: Records to skip (default: 0)
- `limit`: Records to return (default: 20, max: 100)

## Environment Variables
```env
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

## Rate Limiting
- Auth endpoints: 5/min
- File upload: 10/min
- Other endpoints: 100/min

## Support
Contact development team for API support and questions.
