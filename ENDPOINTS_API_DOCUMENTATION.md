# Endpoints API Documentation

## Overview
The Endpoints API provides comprehensive information about all available endpoints in the Tamil Nadu Engineering College Counselling system. This API is designed for administrators to monitor, analyze, and understand the complete API structure.

## Base URL
```
http://localhost:8000/api/v1/endpoints
```

## Authentication
All endpoints require **Admin role** authentication. Include the JWT Bearer token in the Authorization header:
```
Authorization: Bearer <your_admin_token>
```

## API Endpoints

### 1. Get All Endpoints
- **Method:** `GET`
- **Endpoint:** `/api/v1/endpoints/list`
- **Authentication:** Required (Admin role)
- **Description:** Get a comprehensive list of all available endpoints in the system

**Response:**
```json
{
  "message": "All endpoints retrieved successfully",
  "total_endpoints": 45,
  "grouped_by_tags": {
    "Authentication": [
      {
        "path": "/api/v1/auth/register",
        "methods": ["POST"],
        "summary": "Register a new user",
        "tags": ["Authentication"],
        "requires_auth": false,
        "response_model": "dict",
        "full_url": "http://localhost:8000/api/v1/auth/register"
      }
    ],
    "Users": [
      {
        "path": "/api/v1/users/all",
        "methods": ["GET"],
        "summary": "Get all users",
        "tags": ["Users"],
        "requires_auth": true,
        "response_model": "List[UserListResponse]",
        "full_url": "http://localhost:8000/api/v1/users/all"
      }
    ]
  },
  "flat_list": [
    {
      "path": "/api/v1/auth/register",
      "methods": ["POST"],
      "summary": "Register a new user",
      "tags": ["Authentication"],
      "requires_auth": false,
      "response_model": "dict",
      "full_url": "http://localhost:8000/api/v1/auth/register"
    }
  ],
  "statistics": {
    "total_endpoints": 45,
    "authenticated_endpoints": 38,
    "public_endpoints": 7,
    "tags_count": 8,
    "methods_distribution": {
      "GET": 25,
      "POST": 15,
      "PUT": 3,
      "DELETE": 2
    }
  }
}
```

### 2. Get Authenticated Endpoints
- **Method:** `GET`
- **Endpoint:** `/api/v1/endpoints/auth-required`
- **Authentication:** Required (Admin role)
- **Description:** Get list of endpoints that require authentication

**Response:**
```json
{
  "message": "Authenticated endpoints retrieved successfully",
  "total_authenticated_endpoints": 38,
  "endpoints": [
    {
      "path": "/api/v1/users/all",
      "methods": ["GET"],
      "summary": "Get all users",
      "tags": ["Users"],
      "requires_auth": true,
      "response_model": "List[UserListResponse]",
      "full_url": "http://localhost:8000/api/v1/users/all"
    }
  ]
}
```

### 3. Get Public Endpoints
- **Method:** `GET`
- **Endpoint:** `/api/v1/endpoints/public`
- **Authentication:** Required (Admin role)
- **Description:** Get list of public endpoints that don't require authentication

**Response:**
```json
{
  "message": "Public endpoints retrieved successfully",
  "total_public_endpoints": 7,
  "endpoints": [
    {
      "path": "/api/v1/auth/register",
      "methods": ["POST"],
      "summary": "Register a new user",
      "tags": ["Authentication"],
      "requires_auth": false,
      "response_model": "dict",
      "full_url": "http://localhost:8000/api/v1/auth/register"
    },
    {
      "path": "/api/v1/auth/login",
      "methods": ["POST"],
      "summary": "Login user",
      "tags": ["Authentication"],
      "requires_auth": false,
      "response_model": "dict",
      "full_url": "http://localhost:8000/api/v1/auth/login"
    }
  ]
}
```

### 4. Get Endpoints by Tag
- **Method:** `GET`
- **Endpoint:** `/api/v1/endpoints/by-tag/{tag}`
- **Authentication:** Required (Admin role)
- **Description:** Get all endpoints grouped under a specific tag

**Parameters:**
- `tag`: The tag to filter by (e.g., 'Authentication', 'Users', 'Colleges', 'Students', 'Admin', 'Access Control', 'Stages', 'Endpoints')

**Example Request:**
```http
GET /api/v1/endpoints/by-tag/Authentication
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "message": "Endpoints for tag 'Authentication' retrieved successfully",
  "tag": "Authentication",
  "total_endpoints": 10,
  "endpoints": [
    {
      "path": "/api/v1/auth/register",
      "methods": ["POST"],
      "summary": "Register a new user",
      "tags": ["Authentication"],
      "requires_auth": false,
      "response_model": "dict",
      "full_url": "http://localhost:8000/api/v1/auth/register"
    },
    {
      "path": "/api/v1/auth/login",
      "methods": ["POST"],
      "summary": "Login user",
      "tags": ["Authentication"],
      "requires_auth": false,
      "response_model": "dict",
      "full_url": "http://localhost:8000/api/v1/auth/login"
    }
  ]
}
```

### 5. Get All Tags
- **Method:** `GET`
- **Endpoint:** `/api/v1/endpoints/tags`
- **Authentication:** Required (Admin role)
- **Description:** Get list of all available tags in the system

**Response:**
```json
{
  "message": "All tags retrieved successfully",
  "total_tags": 8,
  "tags": [
    {
      "tag": "Authentication",
      "endpoint_count": 10,
      "endpoints": [
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh"
      ]
    },
    {
      "tag": "Users",
      "endpoint_count": 9,
      "endpoints": [
        "/api/v1/users/all",
        "/api/v1/users/admin/profile",
        "/api/v1/users/college/profile"
      ]
    },
    {
      "tag": "Colleges",
      "endpoint_count": 8,
      "endpoints": [
        "/api/v1/colleges/submit",
        "/api/v1/colleges/all",
        "/api/v1/colleges/my-college"
      ]
    },
    {
      "tag": "Students",
      "endpoint_count": 8,
      "endpoints": [
        "/api/v1/students/submit",
        "/api/v1/students/all",
        "/api/v1/students/my-profile"
      ]
    },
    {
      "tag": "Admin",
      "endpoint_count": 1,
      "endpoints": [
        "/api/v1/admin/dashboard-tiles"
      ]
    },
    {
      "tag": "Access Control",
      "endpoint_count": 19,
      "endpoints": [
        "/api/v1/access-control/permissions",
        "/api/v1/access-control/roles",
        "/api/v1/access-control/initialize"
      ]
    },
    {
      "tag": "Stages",
      "endpoint_count": 8,
      "endpoints": [
        "/api/v1/stages/",
        "/api/v1/stages/current",
        "/api/v1/stages/initialize"
      ]
    },
    {
      "tag": "Endpoints",
      "endpoint_count": 6,
      "endpoints": [
        "/api/v1/endpoints/list",
        "/api/v1/endpoints/auth-required",
        "/api/v1/endpoints/public"
      ]
    }
  ]
}
```

### 6. Search Endpoints
- **Method:** `GET`
- **Endpoint:** `/api/v1/endpoints/search`
- **Authentication:** Required (Admin role)
- **Description:** Search endpoints by path, summary, or tags

**Query Parameters:**
- `query`: Search term to look for in endpoint paths, summaries, or tags

**Example Request:**
```http
GET /api/v1/endpoints/search?query=register
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "message": "Search results for 'register'",
  "query": "register",
  "total_results": 3,
  "results": [
    {
      "path": "/api/v1/auth/register",
      "methods": ["POST"],
      "summary": "Register a new user",
      "tags": ["Authentication"],
      "requires_auth": false,
      "response_model": "dict",
      "full_url": "http://localhost:8000/api/v1/auth/register"
    },
    {
      "path": "/api/v1/stages/check-registration/college",
      "methods": ["GET"],
      "summary": "Check if registration is allowed for role",
      "tags": ["Stages"],
      "requires_auth": false,
      "response_model": "dict",
      "full_url": "http://localhost:8000/api/v1/stages/check-registration/college"
    }
  ]
}
```

## Response Schema

### Endpoint Information Object
```json
{
  "path": "string",           // API endpoint path
  "methods": ["string"],      // HTTP methods (GET, POST, PUT, DELETE)
  "summary": "string",        // Endpoint description
  "tags": ["string"],         // Categorization tags
  "requires_auth": "boolean", // Whether authentication is required
  "response_model": "string", // Response model type (if available)
  "full_url": "string"        // Complete URL with base
}
```

### Statistics Object
```json
{
  "total_endpoints": "integer",           // Total number of endpoints
  "authenticated_endpoints": "integer",   // Endpoints requiring auth
  "public_endpoints": "integer",          // Public endpoints
  "tags_count": "integer",                // Number of unique tags
  "methods_distribution": {               // HTTP method distribution
    "GET": "integer",
    "POST": "integer",
    "PUT": "integer",
    "DELETE": "integer"
  }
}
```

## Available Tags

The system categorizes endpoints into the following tags:

1. **Authentication** - User registration, login, password management
2. **Users** - User profile management and administration
3. **Colleges** - College registration and data management
4. **Students** - Student registration and data management
5. **Admin** - Administrative functions and dashboard
6. **Access Control** - Permissions, roles, and system management
7. **Stages** - Stage management and registration control
8. **Endpoints** - Endpoint discovery and management (this API)

## Use Cases

### 1. API Documentation Generation
```bash
# Get all endpoints for documentation
curl -X GET "http://localhost:8000/api/v1/endpoints/list" \
  -H "Authorization: Bearer <admin_token>"
```

### 2. Security Audit
```bash
# Check all authenticated endpoints
curl -X GET "http://localhost:8000/api/v1/endpoints/auth-required" \
  -H "Authorization: Bearer <admin_token>"

# Check all public endpoints
curl -X GET "http://localhost:8000/api/v1/endpoints/public" \
  -H "Authorization: Bearer <admin_token>"
```

### 3. API Analysis
```bash
# Get endpoints by category
curl -X GET "http://localhost:8000/api/v1/endpoints/by-tag/Colleges" \
  -H "Authorization: Bearer <admin_token>"

# Get all available tags
curl -X GET "http://localhost:8000/api/v1/endpoints/tags" \
  -H "Authorization: Bearer <admin_token>"
```

### 4. Endpoint Discovery
```bash
# Search for specific functionality
curl -X GET "http://localhost:8000/api/v1/endpoints/search?query=verify" \
  -H "Authorization: Bearer <admin_token>"
```

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes
- `200 OK`: Request successful
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Admin role required
- `500 Internal Server Error`: Server error

### Example Error Response
```json
{
  "detail": "Error retrieving endpoints: Unable to access route information"
}
```

## Performance Considerations

### Caching
- Consider caching endpoint information for better performance
- Endpoint information rarely changes during runtime
- Cache can be invalidated when new routes are added

### Rate Limiting
- Standard rate limiting applies (100 requests per minute)
- Consider implementing specific limits for search operations

## Security Considerations

### Access Control
- Only admin users can access these endpoints
- Sensitive endpoint information is protected
- Audit logging for endpoint discovery requests

### Information Disclosure
- Be cautious about exposing internal endpoint details
- Consider what information should be visible to admins
- Implement proper access controls

## Integration Examples

### Frontend Dashboard Integration
```javascript
// Get all endpoints for admin dashboard
async function getEndpointsForDashboard() {
  const response = await fetch('/api/v1/endpoints/list', {
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  
  const data = await response.json();
  
  // Display statistics
  displayStatistics(data.statistics);
  
  // Show endpoints by category
  displayEndpointsByCategory(data.grouped_by_tags);
}
```

### API Monitoring Tool
```python
# Monitor API health and structure
import requests

def monitor_api_structure():
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Get all endpoints
    response = requests.get('/api/v1/endpoints/list', headers=headers)
    endpoints = response.json()
    
    # Check for new endpoints
    check_for_new_endpoints(endpoints)
    
    # Monitor endpoint statistics
    monitor_endpoint_statistics(endpoints['statistics'])
```

## Troubleshooting

### Common Issues

#### 1. Empty Endpoint List
- Check if the FastAPI app is properly initialized
- Verify that routes are registered correctly
- Check for import errors in route modules

#### 2. Missing Tags
- Ensure all route decorators include proper tags
- Check for typos in tag names
- Verify route registration order

#### 3. Authentication Issues
- Verify admin token is valid
- Check user role permissions
- Ensure proper authentication middleware

### Debug Information
Enable debug logging to track endpoint discovery issues:
```python
import logging
logging.getLogger("endpoints_api").setLevel(logging.DEBUG)
```

## Future Enhancements

### 1. Advanced Filtering
- Filter by HTTP method
- Filter by authentication requirements
- Filter by response model type

### 2. Endpoint Analytics
- Usage statistics for each endpoint
- Performance metrics
- Error rate tracking

### 3. API Versioning
- Support for multiple API versions
- Version-specific endpoint discovery
- Migration path information

### 4. Documentation Integration
- Link to detailed documentation
- Include example requests/responses
- Provide testing endpoints

---

This documentation provides comprehensive information about the Endpoints API. For additional support or questions, please refer to the main API documentation or contact the development team.
