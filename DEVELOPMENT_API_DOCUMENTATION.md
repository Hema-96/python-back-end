# Development API Documentation

## Overview
The Development API provides temporary access control management for development and testing purposes. This API allows users to quickly gain access to all relevant endpoints based on their role, making development and testing more efficient.

## ⚠️ **IMPORTANT: Development Only**
**This API is intended for development and testing purposes only. It should NOT be used in production environments.**

## Base URL
```
http://localhost:8000/api/v1/development
```

## Authentication
All endpoints require **user authentication** (any logged-in user). Include the JWT Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### 1. Grant All Access
- **Method:** `POST`
- **Endpoint:** `/api/v1/development/grant-all-access`
- **Authentication:** Required (any authenticated user)
- **Description:** Grant all API access to the current user based on their role

**Role-based Access Distribution:**

#### **Admin Users** 🛡️
- **Full Access:** Gets access to ALL endpoints and functions
- **Permissions:** User management, college management, student management, file management, system administration, stage management, access control
- **Use Case:** Complete system testing and administration

#### **College Users** 🏫
- **Limited Access:** Gets access to college-related endpoints and basic user functions
- **Permissions:** 
  - User: read, write
  - College: read, write, delete
  - File: upload, download, delete
  - Stage: read
- **Restricted:** Cannot access admin functions, student management, system administration
- **Use Case:** College functionality testing

#### **Student Users** 👨‍🎓
- **Limited Access:** Gets access to student-related endpoints and basic user functions
- **Permissions:**
  - User: read, write
  - Student: read, write, delete
  - File: upload, download, delete
  - Stage: read
- **Restricted:** Cannot access admin functions, college management, system administration
- **Use Case:** Student functionality testing

**Request:**
```http
POST /api/v1/development/grant-all-access
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "message": "All access granted successfully for admin role",
  "user_id": 1,
  "user_email": "admin@example.com",
  "user_role": "admin",
  "assigned_role": "admin",
  "assigned_permissions": [
    {
      "id": 1,
      "name": "user:read",
      "description": "Read user information",
      "resource_type": "user"
    },
    {
      "id": 2,
      "name": "user:write",
      "description": "Write user information",
      "resource_type": "user"
    },
    {
      "id": 3,
      "name": "college:read",
      "description": "Read college information",
      "resource_type": "college"
    }
  ],
  "total_permissions": 25,
  "development_mode": true,
  "warning": "This is development mode. In production, implement proper RBAC."
}
```

### 2. Reset Access
- **Method:** `POST`
- **Endpoint:** `/api/v1/development/reset-access`
- **Authentication:** Required (any authenticated user)
- **Description:** Reset/Revoke all access for the current user

**What it does:**
1. Removes all role assignments from the user
2. Keeps the user account but with no permissions
3. User will need to re-authenticate or get new permissions

**Request:**
```http
POST /api/v1/development/reset-access
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "message": "All access reset successfully",
  "user_id": 1,
  "user_email": "admin@example.com",
  "removed_roles": 2,
  "current_status": "No roles assigned - no permissions",
  "development_mode": true,
  "note": "User will need to re-authenticate or get new permissions"
}
```

### 3. Get Current Access
- **Method:** `GET`
- **Endpoint:** `/api/v1/development/current-access`
- **Authentication:** Required (any authenticated user)
- **Description:** Get current user's access information including roles and permissions

**Request:**
```http
GET /api/v1/development/current-access
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "role": "admin",
    "is_active": true
  },
  "assigned_roles": [
    {
      "role_id": 1,
      "role_name": "admin",
      "role_description": "Administrator role with full access",
      "permissions": [
        {
          "id": 1,
          "name": "user:read",
          "description": "Read user information",
          "resource_type": "user"
        },
        {
          "id": 2,
          "name": "user:write",
          "description": "Write user information",
          "resource_type": "user"
        }
      ],
      "permission_count": 25
    }
  ],
  "total_permissions": 25,
  "access_summary": "Has access to 25 permissions across 1 roles",
  "development_mode": true,
  "warning": "This is development mode. In production, implement proper RBAC."
}
```

## Permission Categories

### **User Management** 👤
- `user:read` - Read user information
- `user:write` - Write user information  
- `user:delete` - Delete user

### **College Management** 🏫
- `college:read` - Read college information
- `college:write` - Write college information
- `college:delete` - Delete college

### **Student Management** 👨‍🎓
- `student:read` - Read student information
- `student:write` - Write student information
- `student:delete` - Delete student

### **File Management** 📁
- `file:upload` - Upload files
- `file:download` - Download files
- `file:delete` - Delete files

### **System Management** ⚙️
- `system:admin` - System administration
- `system:read` - System read access

### **Stage Management** 📅
- `stage:read` - Read stage information
- `stage:write` - Write stage information
- `stage:admin` - Stage administration

### **Access Control** 🔐
- `access:read` - Read access control
- `access:write` - Write access control
- `access:admin` - Access control administration

## Use Cases

### 1. **Quick Development Setup**
```bash
# Login as any user
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}'

# Grant all access based on role
curl -X POST "http://localhost:8000/api/v1/development/grant-all-access" \
  -H "Authorization: Bearer <jwt_token>"
```

### 2. **Role Testing**
```bash
# Test admin access
curl -X GET "http://localhost:8000/api/v1/development/current-access" \
  -H "Authorization: Bearer <admin_token>"

# Test college access
curl -X GET "http://localhost:8000/api/v1/development/current-access" \
  -H "Authorization: Bearer <college_token>"

# Test student access
curl -X GET "http://localhost:8000/api/v1/development/current-access" \
  -H "Authorization: Bearer <student_token>"
```

### 3. **Access Reset**
```bash
# Reset user access
curl -X POST "http://localhost:8000/api/v1/development/reset-access" \
  -H "Authorization: Bearer <jwt_token>"
```

## Development Workflow

### **Step 1: User Registration/Login**
```bash
# Register or login with any role
POST /api/v1/auth/register
POST /api/v1/auth/login
```

### **Step 2: Grant Development Access**
```bash
# Grant all access based on user role
POST /api/v1/development/grant-all-access
```

### **Step 3: Test Functionality**
```bash
# Now user can access all relevant endpoints based on their role
# Admin: All endpoints
# College: College + basic user endpoints
# Student: Student + basic user endpoints
```

### **Step 4: Reset When Done**
```bash
# Reset access when development is complete
POST /api/v1/development/reset-access
```

## Security Considerations

### **Development Only**
- ⚠️ **NEVER use in production**
- ⚠️ **Bypasses normal RBAC checks**
- ⚠️ **Grants excessive permissions**

### **Role Restrictions**
- **Students cannot see admin access** - They only get student-related permissions
- **Colleges cannot see admin access** - They only get college-related permissions
- **Admins get full access** - For complete system testing

### **Permission Filtering**
- Permissions are filtered based on user role
- Students don't get college or admin permissions
- Colleges don't get student or admin permissions
- Only admins get all permissions

## Error Handling

### **Common Error Responses**

#### **User Has No Role**
```json
{
  "detail": "User has no role assigned"
}
```

#### **Unsupported User Role**
```json
{
  "detail": "Unsupported user role: invalid_role"
}
```

#### **Database Error**
```json
{
  "detail": "Error granting all access: Database connection failed"
}
```

### **HTTP Status Codes**
- `200 OK`: Operation successful
- `400 Bad Request`: Invalid request (e.g., no role assigned)
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Server error

## Integration Examples

### **Frontend Development Helper**
```javascript
// Development helper function
async function grantDevelopmentAccess() {
  try {
    const response = await fetch('/api/v1/development/grant-all-access', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (response.ok) {
      console.log(`Access granted: ${data.total_permissions} permissions`);
      console.log(`Role: ${data.assigned_role}`);
    } else {
      console.error('Failed to grant access:', data.detail);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Reset access when done
async function resetDevelopmentAccess() {
  try {
    const response = await fetch('/api/v1/development/reset-access', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    console.log('Access reset:', data.message);
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### **Testing Script**
```python
import requests

def setup_development_access(base_url, token):
    """Setup development access for testing"""
    headers = {'Authorization': f'Bearer {token}'}
    
    # Grant all access
    response = requests.post(
        f'{base_url}/development/grant-all-access',
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Access granted: {data['total_permissions']} permissions")
        print(f"   Role: {data['assigned_role']}")
        return True
    else:
        print(f"❌ Failed to grant access: {response.json()['detail']}")
        return False

def reset_development_access(base_url, token):
    """Reset development access"""
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.post(
        f'{base_url}/development/reset-access',
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ Access reset successfully")
        return True
    else:
        print(f"❌ Failed to reset access: {response.json()['detail']}")
        return False

# Usage
base_url = "http://localhost:8000/api/v1"
token = "your_jwt_token"

# Setup access
setup_development_access(base_url, token)

# Run your tests here...

# Reset access
reset_development_access(base_url, token)
```

## Best Practices

### **During Development**
1. **Use for testing only** - Don't rely on this for production features
2. **Grant access when needed** - Only when actively testing
3. **Reset when done** - Always reset access after testing
4. **Test role restrictions** - Verify that students/colleges can't access admin functions

### **Before Production**
1. **Remove this API** - Delete or disable before deployment
2. **Implement proper RBAC** - Use the access control system
3. **Test permissions** - Verify normal access control works
4. **Audit access** - Review all user permissions

## Troubleshooting

### **Common Issues**

#### **1. "User has no role assigned"**
- Ensure user has a role set in the database
- Check user registration process
- Verify role field is not null

#### **2. "Unsupported user role"**
- Check if user role matches UserRole enum values
- Verify role values: 1 (admin), 2 (college), 3 (student)

#### **3. Database errors**
- Check database connection
- Verify table structure
- Check for foreign key constraints

#### **4. Permission not working**
- Verify role assignment was successful
- Check permission names in database
- Ensure middleware is checking permissions correctly

### **Debug Steps**
1. Check current access: `GET /development/current-access`
2. Verify user role in database
3. Check role assignments table
4. Verify permissions table
5. Check role-permission mappings

## Future Enhancements

### **1. Temporary Access**
- Add expiration time for granted permissions
- Auto-revoke access after certain time
- Scheduled access cleanup

### **2. Granular Control**
- Allow selective permission granting
- Custom permission sets for different scenarios
- Permission templates for common use cases

### **3. Audit Logging**
- Log all development access grants
- Track who granted what permissions
- Development access history

### **4. Environment Control**
- Disable in production automatically
- Environment variable control
- Feature flag integration

---

## Summary

The Development API provides a quick way to grant role-based access during development:

- **`POST /grant-all-access`** - Grant access based on user role
- **`POST /reset-access`** - Reset all user access
- **`GET /current-access`** - Check current user access

**Key Features:**
- ✅ **Role-based access** - Different permissions for admin/college/student
- ✅ **Students can't see admin access** - Restricted to student functions
- ✅ **Quick setup** - Single API call for full access
- ✅ **Easy reset** - Single API call to remove access
- ✅ **Development only** - Safe for testing, not for production

**Remember:** This is for development purposes only. Always implement proper RBAC for production use!
