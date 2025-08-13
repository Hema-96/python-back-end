# Stage Management System Documentation

## Overview
The Stage Management System is a core feature of the Tamil Nadu Engineering College Counselling platform that controls access to different functionalities based on the current phase of the counselling process. This system ensures that users can only perform actions that are appropriate for the current stage.

## Purpose
The stage system serves several critical purposes:

1. **Controlled Registration**: Prevents users from registering at inappropriate times
2. **Feature Access Control**: Blocks or allows specific endpoints based on current stage
3. **Process Management**: Ensures the counselling process follows a logical sequence
4. **Admin Control**: Gives administrators full control over the application flow

## Stage Types

### 1. Stage 1: College Registration
- **Purpose**: Allow colleges to register and submit their details
- **Duration**: Typically 2-4 weeks
- **Allowed Actions**: College registration, college profile creation, college data submission
- **Blocked Actions**: Student registration, application processing
- **Target Users**: College administrators

### 2. Stage 2: Student Registration
- **Purpose**: Allow students to register and submit their details
- **Duration**: Typically 3-4 weeks
- **Allowed Actions**: Student registration, student profile creation, student data submission
- **Blocked Actions**: College registration, application processing
- **Target Users**: Students

### 3. Stage 3: Application Processing
- **Purpose**: Process applications and verify submitted data
- **Duration**: Typically 2-3 weeks
- **Allowed Actions**: Admin verification, data processing, application review
- **Blocked Actions**: New registrations, data modifications
- **Target Users**: Administrators

### 4. Stage 4: Results and Allotment
- **Purpose**: Display results and handle seat allotment
- **Duration**: Typically 1-2 weeks
- **Allowed Actions**: Result viewing, seat allotment, counselling rounds
- **Blocked Actions**: New registrations, data modifications
- **Target Users**: Students, Colleges, Administrators

### 5. Completed: System Completed
- **Purpose**: Mark the end of the counselling process
- **Duration**: Indefinite
- **Allowed Actions**: View-only access to historical data
- **Blocked Actions**: All modifications and new registrations
- **Target Users**: All users (read-only)

## Database Schema

### Stage Table
```sql
CREATE TABLE stage (
    id SERIAL PRIMARY KEY,
    stage_type VARCHAR(20) NOT NULL, -- stage_1, stage_2, stage_3, stage_4, completed
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
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
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### 1. Create Stage
```http
POST /api/v1/stages/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "stage_type": "stage_1",
  "name": "College Registration Phase",
  "description": "Colleges can register and submit their details",
  "is_active": false,
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z",
  "allowed_roles": ["college"],
  "blocked_endpoints": [
    "/api/v1/students/submit",
    "/api/v1/students/register"
  ],
  "required_permissions": ["college_register"]
}
```

**Response:**
```json
{
  "id": 1,
  "stage_type": "stage_1",
  "name": "College Registration Phase",
  "description": "Colleges can register and submit their details",
  "is_active": false,
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z",
  "allowed_roles": ["college"],
  "blocked_endpoints": ["/api/v1/students/submit", "/api/v1/students/register"],
  "required_permissions": ["college_register"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": 1
}
```

### 2. Get All Stages
```http
GET /api/v1/stages/
Authorization: Bearer <admin_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "stage_type": "stage_1",
    "name": "College Registration Phase",
    "description": "Colleges can register and submit their details",
    "is_active": true,
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z",
    "allowed_roles": ["college"],
    "blocked_endpoints": ["/api/v1/students/submit"],
    "required_permissions": ["college_register"],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": 1
  }
]
```

### 3. Get Current Stage Information
```http
GET /api/v1/stages/current
```

**Response:**
```json
{
  "current_stage": {
    "id": 1,
    "stage_type": "stage_1",
    "name": "College Registration Phase",
    "description": "Colleges can register and submit their details",
    "is_active": true,
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z",
    "allowed_roles": ["college"],
    "blocked_endpoints": ["/api/v1/students/submit"],
    "required_permissions": ["college_register"],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": 1
  },
  "allowed_actions": ["college_registration", "college_profile_creation"],
  "blocked_actions": ["student_registration", "student_profile_creation"],
  "stage_info": {
    "message": "College Registration Phase is currently active",
    "description": "Colleges can register and submit their details",
    "days_remaining": 15,
    "progress_percentage": 50
  }
}
```

### 4. Update Stage
```http
PUT /api/v1/stages/1
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Updated College Registration Phase",
  "description": "Updated description for college registration",
  "is_active": true,
  "end_date": "2024-02-15T23:59:59Z"
}
```

### 5. Activate Stage
```http
POST /api/v1/stages/1/activate
Authorization: Bearer <admin_token>
```

**Important**: This will automatically deactivate all other stages.

### 6. Deactivate Stage
```http
POST /api/v1/stages/1/deactivate
Authorization: Bearer <admin_token>
```

### 7. Initialize Default Stages
```http
POST /api/v1/stages/initialize
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "message": "Default stages initialized successfully",
  "stage_ids": [1, 2, 3, 4, 5],
  "stages_created": 5,
  "stages": [
    {
      "id": 1,
      "name": "College Registration",
      "stage_type": "stage_1"
    },
    {
      "id": 2,
      "name": "Student Registration",
      "stage_type": "stage_2"
    },
    {
      "id": 3,
      "name": "Application Processing",
      "stage_type": "stage_3"
    },
    {
      "id": 4,
      "name": "Results and Allotment",
      "stage_type": "stage_4"
    },
    {
      "id": 5,
      "name": "System Completed",
      "stage_type": "completed"
    }
  ]
}
```

### 8. Check Registration Allowed
```http
GET /api/v1/stages/check-registration/college
```

**Response:**
```json
{
  "allowed": true,
  "current_stage": {
    "id": 1,
    "stage_type": "stage_1",
    "name": "College Registration Phase",
    "description": "Colleges can register and submit their details",
    "is_active": true
  },
  "message": "College Registration Phase is currently active",
  "description": "Colleges can register and submit their details",
  "allowed_actions": ["college_registration"],
  "blocked_actions": ["student_registration"],
  "days_remaining": 15
}
```

## Stage Configuration

### Allowed Roles
Specify which user roles are allowed during each stage:
```json
{
  "allowed_roles": ["college", "admin"]
}
```

### Blocked Endpoints
Specify which API endpoints should be blocked during each stage:
```json
{
  "blocked_endpoints": [
    "/api/v1/students/submit",
    "/api/v1/students/register",
    "/api/v1/colleges/verify"
  ]
}
```

### Required Permissions
Specify additional permissions required during each stage:
```json
{
  "required_permissions": [
    "college_register",
    "college_submit_data"
  ]
}
```

## Stage Transitions

### Typical Stage Flow
1. **Stage 1** → **Stage 2**: After college registration period ends
2. **Stage 2** → **Stage 3**: After student registration period ends
3. **Stage 3** → **Stage 4**: After application processing is complete
4. **Stage 4** → **Completed**: After results and allotment are finalized

### Manual Stage Management
Admins can manually control stage transitions:
```bash
# Activate Stage 1
curl -X POST /api/v1/stages/1/activate

# Activate Stage 2 (automatically deactivates Stage 1)
curl -X POST /api/v1/stages/2/activate

# Deactivate current stage
curl -X POST /api/v1/stages/1/deactivate
```

## Middleware Integration

### Stage Access Middleware
The system includes middleware that automatically checks stage-based access:

```python
async def stage_access_middleware(request: Request, call_next):
    # Skip stage checks for certain endpoints
    skip_paths = [
        "/docs", "/redoc", "/openapi.json",
        "/api/v1/stages/current",
        "/api/v1/stages/check-registration",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh"
    ]
    
    if any(request.url.path.startswith(path) for path in skip_paths):
        return await call_next(request)
    
    # Check if endpoint is blocked in current stage
    current_stage = stage_service.get_current_stage()
    if current_stage and request.url.path in current_stage.blocked_endpoints:
        return JSONResponse(
            status_code=403,
            content={
                "message": "Endpoint blocked in current stage",
                "current_stage": current_stage.name,
                "description": current_stage.description
            }
        )
    
    return await call_next(request)
```

## Registration Control

### Stage-Based Registration Logic
```python
def is_registration_allowed(user_role: UserRole) -> bool:
    current_stage = get_current_stage()
    
    if not current_stage:
        return False  # No active stage
    
    # Check if user role is allowed in current stage
    if user_role.value not in current_stage.allowed_roles:
        return False
    
    # Check stage-specific rules
    if current_stage.stage_type == "stage_1":
        return user_role == UserRole.COLLEGE
    elif current_stage.stage_type == "stage_2":
        return user_role == UserRole.STUDENT
    else:
        return False  # No registration in other stages
```

### Registration Error Response
When registration is not allowed:
```json
{
  "detail": {
    "message": "Registration not allowed in current stage",
    "current_stage": "Application Processing",
    "description": "Processing applications and verifying data",
    "allowed_actions": ["admin_verification", "data_processing"],
    "blocked_actions": ["college_registration", "student_registration"]
  }
}
```

## Admin Dashboard Integration

### Stage Management Interface
Admins can manage stages through the dashboard:

1. **View Current Stage**: See which stage is currently active
2. **Stage Timeline**: View all stages and their status
3. **Manual Control**: Activate/deactivate stages manually
4. **Stage Configuration**: Modify stage settings and permissions
5. **Progress Tracking**: Monitor stage progress and time remaining

### Stage Statistics
```json
{
  "current_stage": {
    "name": "College Registration",
    "days_remaining": 15,
    "progress_percentage": 50,
    "registrations_count": 125,
    "pending_verifications": 45
  },
  "next_stage": {
    "name": "Student Registration",
    "estimated_start": "2024-02-01T00:00:00Z"
  },
  "stage_history": [
    {
      "stage": "College Registration",
      "started": "2024-01-01T00:00:00Z",
      "ended": null,
      "status": "active"
    }
  ]
}
```

## Best Practices

### 1. Stage Planning
- Plan stage durations based on expected user volume
- Consider buffer time between stages
- Set realistic deadlines for each phase

### 2. Communication
- Clearly communicate stage changes to users
- Provide advance notice before stage transitions
- Use multiple channels (email, SMS, notifications)

### 3. Monitoring
- Monitor registration numbers during each stage
- Track verification progress
- Adjust stage durations if needed

### 4. Backup Plans
- Have contingency plans for stage extensions
- Prepare for manual stage management if needed
- Keep backup admin accounts for stage control

## Troubleshooting

### Common Issues

#### 1. Stage Not Activating
```bash
# Check if another stage is active
GET /api/v1/stages/

# Force deactivate all stages
POST /api/v1/stages/1/deactivate
POST /api/v1/stages/2/deactivate
# ... repeat for all stages

# Then activate desired stage
POST /api/v1/stages/1/activate
```

#### 2. Registration Blocked Unexpectedly
```bash
# Check current stage
GET /api/v1/stages/current

# Check registration status for specific role
GET /api/v1/stages/check-registration/college
```

#### 3. Endpoint Access Issues
```bash
# Check blocked endpoints in current stage
GET /api/v1/stages/current

# Verify endpoint is not in blocked_endpoints list
```

### Debug Information
Enable debug logging to track stage-related issues:
```python
import logging
logging.getLogger("stage_service").setLevel(logging.DEBUG)
```

## Security Considerations

### 1. Admin Access Control
- Only super admins should have stage management permissions
- Implement audit logging for stage changes
- Require confirmation for critical stage transitions

### 2. Data Integrity
- Prevent data modifications during inappropriate stages
- Implement proper validation for stage transitions
- Backup stage configuration before major changes

### 3. User Experience
- Provide clear error messages when actions are blocked
- Show stage information in user interface
- Allow users to check their access status

## Future Enhancements

### 1. Automated Transitions
- Implement time-based automatic stage transitions
- Add conditions for automatic stage progression
- Include notification systems for stage changes

### 2. Advanced Permissions
- Implement role-based stage permissions
- Add granular endpoint control
- Support for custom stage types

### 3. Analytics and Reporting
- Stage completion analytics
- User behavior tracking during stages
- Performance metrics for each stage

### 4. Integration Features
- Calendar integration for stage scheduling
- Email/SMS notifications for stage changes
- API webhooks for stage events

## Support and Maintenance

### Regular Maintenance Tasks
1. **Monitor Stage Progress**: Check stage completion rates
2. **Update Stage Configurations**: Modify settings as needed
3. **Backup Stage Data**: Regular backups of stage configurations
4. **Performance Monitoring**: Track system performance during stages

### Contact Information
For stage management support:
- **Technical Issues**: Development Team
- **Configuration Help**: System Administrators
- **User Access Issues**: Support Team

---

This documentation provides comprehensive information about the Stage Management System. For additional support or questions, please refer to the main API documentation or contact the development team.
