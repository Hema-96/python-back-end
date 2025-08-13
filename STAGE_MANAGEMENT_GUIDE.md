# Stage Management System Guide

## Overview

The Stage Management System provides admin controls based on stages to manage the application lifecycle. It allows administrators to control access to different features based on the current stage of the application.

## Stages

The system supports the following stages:

### Stage 1: College Registration
- **Purpose**: Colleges can register and submit their details
- **Allowed Actions**: College registration, college login, college profile updates
- **Blocked Actions**: Student registration, student login
- **Duration**: Until admin manually ends this stage

### Stage 2: Student Registration
- **Purpose**: Students can register and submit their details
- **Allowed Actions**: Student registration, student login, student profile updates
- **Blocked Actions**: College registration, college login
- **Duration**: Until admin manually ends this stage

### Stage 3: Application Processing
- **Purpose**: Applications are being processed and reviewed
- **Allowed Actions**: Application processing, admin review
- **Blocked Actions**: All registrations
- **Duration**: Until admin manually ends this stage

### Stage 4: Results and Allotment
- **Purpose**: Results are published and allotments are made
- **Allowed Actions**: Results viewing, allotment viewing
- **Blocked Actions**: All registrations, application processing
- **Duration**: Until admin manually ends this stage

### Completed: System Completed
- **Purpose**: All stages completed
- **Allowed Actions**: View-only access for admins
- **Blocked Actions**: All registrations, all processing
- **Duration**: Permanent

## API Endpoints

### Stage Management (Admin Only)

#### Get Current Stage Information
```http
GET /api/v1/stages/current
```
**Public endpoint** - No authentication required
**Response**: Information about current stage, allowed/blocked actions

#### Check Registration Status
```http
GET /api/v1/stages/check-registration/{role}
```
**Public endpoint** - No authentication required
**Parameters**: `role` (college, student, admin)
**Response**: Whether registration is allowed for the specified role

#### Get All Stages
```http
GET /api/v1/stages/
```
**Required Role**: Admin
**Response**: List of all stages in the system

#### Create Stage
```http
POST /api/v1/stages/
```
**Required Role**: Admin
**Body**: Stage creation data
**Response**: Created stage information

#### Update Stage
```http
PUT /api/v1/stages/{stage_id}
```
**Required Role**: Admin
**Body**: Stage update data
**Response**: Updated stage information

#### Activate Stage
```http
POST /api/v1/stages/{stage_id}/activate
```
**Required Role**: Admin
**Response**: Activated stage information
**Note**: Automatically deactivates all other stages

#### Deactivate Stage
```http
POST /api/v1/stages/{stage_id}/deactivate
```
**Required Role**: Admin
**Response**: Deactivated stage information

#### Initialize Default Stages
```http
POST /api/v1/stages/initialize
```
**Required Role**: Admin
**Response**: Information about created stages
**Note**: Creates all 5 default stages if they don't exist

## Stage-Based Access Control

### Registration Control

The registration endpoint (`/api/v1/auth/register`) automatically checks the current stage:

- **Stage 1**: Only college registration allowed
- **Stage 2**: Only student registration allowed
- **Other stages**: No registration allowed

### Endpoint Blocking

The stage middleware automatically blocks endpoints based on the current stage configuration:

- **Blocked endpoints** are defined per stage
- **Public endpoints** are always accessible (docs, health checks, etc.)
- **Admin endpoints** are not affected by stage restrictions

### Middleware Integration

The stage access middleware is automatically applied to all requests and:

1. Checks if the requested endpoint is blocked in the current stage
2. Returns appropriate error messages with stage information
3. Allows the request to proceed if no restrictions apply

## Usage Examples

### 1. Starting College Registration Phase

```bash
# Get all stages
curl -X GET "http://localhost:8000/api/v1/stages/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Activate Stage 1 (College Registration)
curl -X POST "http://localhost:8000/api/v1/stages/1/activate" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 2. Checking Current Stage

```bash
# Get current stage information
curl -X GET "http://localhost:8000/api/v1/stages/current"

# Check if college registration is allowed
curl -X GET "http://localhost:8000/api/v1/stages/check-registration/college"
```

### 3. Transitioning to Student Registration

```bash
# Activate Stage 2 (Student Registration)
curl -X POST "http://localhost:8000/api/v1/stages/2/activate" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 4. Registration Attempts

```bash
# College registration (allowed in Stage 1, blocked in Stage 2)
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "college@example.com",
    "password": "password123",
    "role": 2
  }'

# Student registration (blocked in Stage 1, allowed in Stage 2)
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123",
    "role": 3
  }'
```

## Error Responses

### Registration Blocked
```json
{
  "detail": {
    "message": "Registration not allowed in current stage",
    "current_stage": "College Registration Phase",
    "description": "Colleges can register and submit their details",
    "allowed_actions": ["college_registration", "college_login", "college_profile_update"],
    "blocked_actions": ["student_registration", "student_login"]
  }
}
```

### Endpoint Blocked
```json
{
  "message": "Endpoint blocked in current stage",
  "current_stage": "Student Registration",
  "description": "Students can register and submit their details",
  "blocked_endpoints": ["/api/v1/auth/register/college", "/api/v1/colleges/submit"]
}
```

## Database Schema

### Stage Table
```sql
CREATE TABLE stage (
    id SERIAL PRIMARY KEY,
    stage_type VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    is_active BOOLEAN DEFAULT FALSE,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    created_by INTEGER,
    allowed_roles JSON DEFAULT '[]',
    blocked_endpoints JSON DEFAULT '[]',
    required_permissions JSON DEFAULT '[]'
);
```

### StagePermission Table
```sql
CREATE TABLE stage_permission (
    id SERIAL PRIMARY KEY,
    stage_id INTEGER REFERENCES stage(id),
    permission_id INTEGER REFERENCES permission(id),
    is_allowed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL
);
```

## Configuration

### Default Stage Configuration

The system automatically creates 5 default stages with the following configuration:

1. **Stage 1 (College Registration)**:
   - Allowed roles: `["college"]`
   - Blocked endpoints: `["/api/v1/auth/register/student", "/api/v1/students/submit"]`

2. **Stage 2 (Student Registration)**:
   - Allowed roles: `["student"]`
   - Blocked endpoints: `["/api/v1/auth/register/college", "/api/v1/colleges/submit"]`

3. **Stage 3 (Application Processing)**:
   - Allowed roles: `["admin"]`
   - Blocked endpoints: `["/api/v1/auth/register"]`

4. **Stage 4 (Results and Allotment)**:
   - Allowed roles: `["admin", "college", "student"]`
   - Blocked endpoints: `["/api/v1/auth/register", "/api/v1/colleges/submit", "/api/v1/students/submit"]`

5. **Completed**:
   - Allowed roles: `["admin"]`
   - Blocked endpoints: `["/api/v1/auth/register", "/api/v1/colleges/submit", "/api/v1/students/submit"]`

## Security Considerations

1. **Admin Access**: Only users with admin role can manage stages
2. **Stage Transitions**: Only one stage can be active at a time
3. **Audit Logging**: All stage changes are logged for audit purposes
4. **Public Endpoints**: Certain endpoints (docs, health checks) are always accessible
5. **Graceful Degradation**: If stage checks fail, the system continues to function

## Troubleshooting

### Common Issues

1. **No Active Stage**: If no stage is active, all registrations are blocked
2. **Duplicate Stages**: The system prevents duplicate stage types
3. **Permission Errors**: Ensure admin role is properly assigned
4. **Database Issues**: Check database connectivity and table existence

### Debug Commands

```bash
# Check current stage
curl -X GET "http://localhost:8000/api/v1/stages/current"

# List all stages
curl -X GET "http://localhost:8000/api/v1/stages/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Test registration status
curl -X GET "http://localhost:8000/api/v1/stages/check-registration/college"
```

## Integration with Existing System

The stage management system integrates seamlessly with the existing access control system:

1. **RBAC Integration**: Stages work alongside role-based access control
2. **Middleware Integration**: Automatic endpoint blocking based on current stage
3. **API Integration**: All existing APIs respect stage restrictions
4. **Database Integration**: Uses existing database infrastructure

## Future Enhancements

1. **Scheduled Stage Transitions**: Automatic stage transitions based on time
2. **Stage Notifications**: Email/SMS notifications when stages change
3. **Stage Analytics**: Track usage patterns during different stages
4. **Custom Stage Types**: Allow creation of custom stage types
5. **Stage Templates**: Predefined stage configurations for different scenarios
