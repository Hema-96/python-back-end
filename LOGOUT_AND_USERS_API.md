# Logout and Admin Users API Documentation

## Overview

This document describes the newly implemented logout API with token expiration and the admin users list API.

## 1. Logout API

### Endpoint: `POST /api/v1/auth/logout`

### Description
Logs out a user and invalidates their current authentication token by adding it to a blacklist. This ensures that the token cannot be used for future requests even if it hasn't expired yet.

### Authentication
- **Required**: Valid Bearer token in Authorization header
- **Role**: Any authenticated user

### Request
```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

### Response
```json
{
  "message": "Successfully logged out",
  "token_invalidated": true
}
```

### Features
- **Token Blacklisting**: The current token is added to an in-memory blacklist
- **Immediate Invalidation**: Token becomes unusable immediately after logout
- **Security**: Prevents token reuse even if the token hasn't expired

### Usage Example
```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 2. Admin Users List API

### Endpoint: `GET /api/v1/users/all`

### Description
Retrieves a comprehensive list of all users in the system (excluding admin users) with detailed information including roles, status, and profile data. This endpoint supports multiple formats and is designed for admin dashboard functionality.

### Authentication
- **Required**: Valid Bearer token in Authorization header
- **Role**: Admin only (Role 1)

### Request
```http
GET /api/v1/users/all?format=dashboard
Authorization: Bearer <admin_access_token>
```

### Query Parameters
- **format**: Response format (`standard` or `dashboard`)
  - `standard`: Returns UserListResponse objects (default)
  - `dashboard`: Returns formatted data for admin dashboard
- **skip**: Number of records to skip (pagination)
- **limit**: Number of records to return (pagination)
- **role**: Filter by user role
- **is_active**: Filter by active status

### Response Format
```json
{
  "data": [
    {
      "id": "1",
      "name": "John Doe",
      "email": "john@university.edu",
      "role": "student",
      "status": "active",
      "lastLogin": "2 hours ago",
      "registrationDate": "2024-01-15",
      "phone": "+1 (555) 123-4567"
    },
    {
      "id": "3",
      "name": "University Health Center",
      "email": "health@university.edu",
      "role": "college",
      "status": "approved",
      "lastLogin": "3 hours ago",
      "registrationDate": "2024-01-10",
      "phone": "+1 (555) 234-5678",
      "institution": "University Health Center"
    }
  ]
}
```

### User Status Logic
- **Student**: "active" if `is_active` is true, "inactive" otherwise
- **College**: 
  - "approved" if college profile is approved
  - "pending" if not approved
  - "inactive" if user is not active
- **Admin users are excluded** from the results

### Last Login Formatting
- "Just now" for recent logins (< 1 minute)
- "X minutes ago" for logins within the last hour
- "X hours ago" for logins within the last day
- "X days ago" for older logins
- "Never" if no login recorded

### Usage Examples

#### Dashboard Format (for admin dashboard):
```bash
curl -X GET "http://localhost:8000/api/v1/users/all?format=dashboard" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

#### Standard Format (with pagination):
```bash
curl -X GET "http://localhost:8000/api/v1/users/all?skip=0&limit=20" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

#### Filtered by Role:
```bash
curl -X GET "http://localhost:8000/api/v1/users/all?role=student&format=dashboard" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

## 3. Token Blacklist Implementation

### Overview
The logout functionality uses an in-memory token blacklist to immediately invalidate tokens.

### Features
- **In-Memory Storage**: Tokens are stored in a Python set for fast lookup
- **Automatic Checking**: All token verification checks the blacklist
- **Simple Implementation**: No external dependencies required

### Security Considerations
- **Memory-Based**: Blacklist is cleared when server restarts
- **Production Recommendation**: Consider using Redis or database with TTL for production
- **Token Validation**: All protected endpoints automatically check blacklist

### Code Structure
```python
# Token blacklist (in-memory)
_token_blacklist: Set[str] = set()

def add_to_blacklist(token: str) -> None:
    """Add token to blacklist"""
    _token_blacklist.add(token)

def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    return token in _token_blacklist
```

## 4. Testing

### Test Script
Use the provided `test_logout_and_users_api.py` script to test both APIs:

```bash
python test_logout_and_users_api.py
```

### Test Coverage
1. **Login and Logout Flow**
   - Login with valid credentials
   - Verify token works
   - Logout and invalidate token
   - Verify token is no longer valid

2. **Admin Users List**
   - Login as admin
   - Fetch all users
   - Verify response format
   - Check user status logic

3. **Access Control**
   - Verify non-admin users cannot access admin endpoints
   - Verify unauthenticated requests are blocked

## 5. Error Handling

### Logout API Errors
- **401 Unauthorized**: Invalid or missing token
- **500 Internal Server Error**: Server-side error during logout

### Admin Users API Errors
- **401 Unauthorized**: Invalid token or non-admin user
- **500 Internal Server Error**: Database or server error

## 6. Integration Notes

### Frontend Integration
- Call logout API when user clicks logout
- Clear local storage/cookies after successful logout
- Redirect to login page after logout

### Admin Dashboard Integration
- Use the users list API to populate user management tables
- Display user status with appropriate styling
- Show last login times for user activity monitoring

### Security Best Practices
- Always call logout API when user logs out
- Don't store sensitive tokens in localStorage
- Implement automatic token refresh for long sessions
- Consider implementing session timeout warnings
