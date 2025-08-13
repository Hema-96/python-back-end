# Access Control System Guide

## Overview

The Access Control System provides comprehensive role-based access control (RBAC) for the Tamil Nadu Engineering College Counselling Backend API. It includes granular permissions, role management, audit logging, and endpoint protection.

## 🏗️ System Architecture

### Core Components

1. **Permissions**: Granular access rights for specific resources
2. **Roles**: Groups of permissions assigned to users
3. **Users**: System users with assigned roles
4. **Audit Logs**: Complete access tracking and security monitoring
5. **Session Management**: User session tracking and security

### Database Tables

- `permissions`: Individual permissions with resource types and actions
- `roles`: Role definitions and metadata
- `role_permissions`: Many-to-many relationship between roles and permissions
- `user_roles`: Many-to-many relationship between users and roles
- `endpoint_access`: Endpoint-specific access control rules
- `access_logs`: Comprehensive audit trail
- `session_logs`: User session tracking

## 🔐 Permission System

### Permission Types

- **READ**: View data
- **WRITE**: Create/update data
- **DELETE**: Remove data
- **UPDATE**: Modify existing data
- **APPROVE**: Approve/reject submissions
- **VERIFY**: Verify data authenticity
- **ADMIN**: Full administrative access

### Resource Types

- **USER**: User management
- **COLLEGE**: College data management
- **STUDENT**: Student data management
- **ADMIN**: Administrative functions
- **AUTH**: Authentication operations
- **FILE**: File operations
- **SYSTEM**: System-level operations

### Permission Naming Convention

Permissions follow the pattern: `{resource_type}_{permission_type}`

Examples:
- `user_read` - Read user data
- `college_approve` - Approve college submissions
- `student_verify` - Verify student documents
- `system_admin` - Full system administration

## 👥 Role System

### Default Roles

1. **super_admin**: Full system access with all permissions
2. **admin**: Administrative access with management permissions
3. **college_admin**: College-specific administrative access
4. **student**: Student user with limited access
5. **viewer**: Read-only access

### Role Hierarchy

```
super_admin
├── admin
│   ├── college_admin
│   └── viewer
└── student
```

## 🚀 Getting Started

### 1. Initialize the System

After setting up the database, initialize the access control system:

```bash
# Login as admin
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@tncounselling.com",
    "password": "admin123"
  }'

# Initialize access control system
curl -X POST "http://localhost:8000/api/v1/access-control/initialize" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. Create Custom Roles

```bash
# Create a new role
curl -X POST "http://localhost:8000/api/v1/access-control/roles" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "college_verifier",
    "description": "College data verifier with approval rights",
    "is_system_role": false
  }'
```

### 3. Assign Permissions to Roles

```bash
# Assign permission to role
curl -X POST "http://localhost:8000/api/v1/access-control/roles/{role_id}/permissions" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "permission_id": 1,
    "expires_at": null
  }'
```

### 4. Assign Roles to Users

```bash
# Assign role to user
curl -X POST "http://localhost:8000/api/v1/access-control/users/{user_id}/roles" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": 1,
    "expires_at": null
  }'
```

## 📋 API Endpoints

### Permission Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/access-control/permissions` | Create permission |
| GET | `/api/v1/access-control/permissions` | List permissions |
| GET | `/api/v1/access-control/permissions/{id}` | Get permission |
| PUT | `/api/v1/access-control/permissions/{id}` | Update permission |

### Role Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/access-control/roles` | Create role |
| GET | `/api/v1/access-control/roles` | List roles |
| GET | `/api/v1/access-control/roles/{id}` | Get role |
| PUT | `/api/v1/access-control/roles/{id}` | Update role |

### Role-Permission Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/access-control/roles/{id}/permissions` | Assign permission to role |
| DELETE | `/api/v1/access-control/roles/{id}/permissions/{perm_id}` | Remove permission from role |

### User-Role Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/access-control/users/{id}/roles` | Assign role to user |
| DELETE | `/api/v1/access-control/users/{id}/roles/{role_id}` | Remove role from user |

### Bulk Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/access-control/users/bulk-assign-role` | Bulk assign role to users |
| POST | `/api/v1/access-control/roles/bulk-assign-permission` | Bulk assign permission to roles |

### Permission Checking

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/access-control/check-permission` | Check user permission |
| GET | `/api/v1/access-control/users/{id}/permissions` | Get user permissions |

### System Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/access-control/initialize` | Initialize system |
| GET | `/api/v1/access-control/health` | System health check |

## 🔍 Permission Checking Examples

### Check User Permission

```bash
curl -X POST "http://localhost:8000/api/v1/access-control/check-permission" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "resource_type": "college",
    "permission_type": "approve",
    "resource_id": null
  }'
```

Response:
```json
{
  "has_permission": true,
  "required_permissions": ["college_approve", "college_admin"],
  "user_permissions": ["college_read", "college_write", "college_approve"],
  "user_roles": ["admin", "college_admin"]
}
```

### Get User Permissions

```bash
curl -X GET "http://localhost:8000/api/v1/access-control/users/1/permissions" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "user_id": 1,
  "permissions": ["user_read", "college_read", "college_write", "college_approve"],
  "roles": ["admin", "college_admin"]
}
```

## 📊 Audit Logging

The system automatically logs all access attempts with the following information:

- User ID and authentication status
- Endpoint path and HTTP method
- Request IP and user agent
- Action performed (READ, CREATE, UPDATE, DELETE, etc.)
- Resource type and ID
- Success/failure status
- Error messages
- Response status codes
- Execution time

### View Audit Logs

```bash
curl -X GET "http://localhost:8000/api/v1/access-control/audit-logs" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -G \
  -d "skip=0" \
  -d "limit=50" \
  -d "user_id=1" \
  -d "action=login"
```

## 🔧 Middleware Integration

The access control system includes middleware for automatic endpoint protection:

### Features

1. **Automatic Permission Checking**: Validates user permissions for each endpoint
2. **Access Logging**: Logs all access attempts automatically
3. **IP Tracking**: Records client IP addresses
4. **Performance Monitoring**: Tracks execution times
5. **Error Handling**: Graceful handling of access violations

### Configuration

The middleware automatically skips access control for:
- Documentation endpoints (`/docs`, `/redoc`)
- Health check endpoints (`/health`)
- Public authentication endpoints (login, register, password reset)

## 🛡️ Security Best Practices

### 1. Principle of Least Privilege

- Assign only necessary permissions to roles
- Use role expiration dates for temporary access
- Regularly review and audit permissions

### 2. Role Design

- Create specific roles for different user types
- Avoid overly broad permissions
- Use hierarchical role structure

### 3. Monitoring

- Regularly review audit logs
- Monitor for unusual access patterns
- Set up alerts for security events

### 4. Session Management

- Implement session timeouts
- Track active sessions
- Force logout on security events

## 🔄 Bulk Operations

### Bulk Role Assignment

```bash
curl -X POST "http://localhost:8000/api/v1/access-control/users/bulk-assign-role" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [1, 2, 3, 4, 5],
    "role_id": 2,
    "expires_at": "2024-12-31T23:59:59Z"
  }'
```

### Bulk Permission Assignment

```bash
curl -X POST "http://localhost:8000/api/v1/access-control/roles/bulk-assign-permission" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_ids": [1, 2, 3],
    "permission_id": 5,
    "expires_at": null
  }'
```

## 🚨 Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   - Check user roles and permissions
   - Verify permission assignments
   - Check role expiration dates

2. **Database Errors**
   - Ensure all tables are created
   - Check database connectivity
   - Verify foreign key constraints

3. **Performance Issues**
   - Monitor audit log table size
   - Implement log rotation
   - Optimize database queries

### Debug Commands

```bash
# Check system health
curl -X GET "http://localhost:8000/api/v1/access-control/health" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get all permissions
curl -X GET "http://localhost:8000/api/v1/access-control/permissions" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get all roles
curl -X GET "http://localhost:8000/api/v1/access-control/roles" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📈 Performance Considerations

1. **Caching**: Consider caching user permissions for better performance
2. **Indexing**: Ensure proper database indexes on frequently queried columns
3. **Log Rotation**: Implement log rotation to prevent database bloat
4. **Connection Pooling**: Use database connection pooling for better performance

## 🔮 Future Enhancements

1. **Dynamic Permission Loading**: Load permissions from configuration files
2. **Permission Inheritance**: Implement permission inheritance between roles
3. **Time-based Access**: Add time-based access control
4. **Geographic Restrictions**: Implement location-based access control
5. **Multi-factor Authentication**: Integrate with MFA systems
6. **API Rate Limiting**: Add rate limiting based on user roles

## 📞 Support

For issues or questions about the access control system:

1. Check the audit logs for error details
2. Review the system health endpoint
3. Verify database connectivity and table structure
4. Contact the development team with specific error messages
