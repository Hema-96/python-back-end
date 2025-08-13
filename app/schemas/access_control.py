from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.models.access_control import (
    PermissionType, ResourceType, AuditAction, StageType
)

class PermissionType(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    UPDATE = "update"
    APPROVE = "approve"
    VERIFY = "verify"
    ADMIN = "admin"

class ResourceType(str, Enum):
    USER = "user"
    COLLEGE = "college"
    STUDENT = "student"
    ADMIN = "admin"
    AUTH = "auth"
    FILE = "file"
    SYSTEM = "system"

class AuditAction(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    VERIFY = "verify"
    UPLOAD = "upload"
    DOWNLOAD = "download"

# Permission Schemas
class PermissionBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    resource_type: ResourceType
    permission_type: PermissionType
    is_active: bool = True

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    resource_type: Optional[ResourceType] = None
    permission_type: Optional[PermissionType] = None
    is_active: Optional[bool] = None

class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Role Schemas
class RoleBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_system_role: bool = False
    is_active: bool = True

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Role Permission Schemas
class RolePermissionBase(BaseModel):
    role_id: int
    permission_id: int
    expires_at: Optional[datetime] = None
    is_active: bool = True

class RolePermissionCreate(RolePermissionBase):
    pass

class RolePermissionUpdate(BaseModel):
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class RolePermissionResponse(RolePermissionBase):
    id: int
    granted_by: Optional[int] = None
    granted_at: datetime

    class Config:
        from_attributes = True

# User Role Schemas
class UserRoleAssignmentBase(BaseModel):
    user_id: int
    role_id: int
    expires_at: Optional[datetime] = None
    is_active: bool = True

class UserRoleAssignmentCreate(UserRoleAssignmentBase):
    pass

class UserRoleAssignmentUpdate(BaseModel):
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class UserRoleAssignmentResponse(UserRoleAssignmentBase):
    id: int
    assigned_by: Optional[int] = None
    assigned_at: datetime

    class Config:
        from_attributes = True

# Endpoint Access Schemas
class EndpointAccessBase(BaseModel):
    endpoint_path: str = Field(..., max_length=500)
    http_method: str = Field(..., max_length=10)
    required_permissions: List[str] = Field(default=[])
    required_roles: List[str] = Field(default=[])
    is_public: bool = False
    is_active: bool = True

class EndpointAccessCreate(EndpointAccessBase):
    pass

class EndpointAccessUpdate(BaseModel):
    endpoint_path: Optional[str] = Field(None, max_length=500)
    http_method: Optional[str] = Field(None, max_length=10)
    required_permissions: Optional[List[str]] = None
    required_roles: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None

class EndpointAccessResponse(EndpointAccessBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Access Log Schemas
class AccessLogBase(BaseModel):
    endpoint_path: str = Field(..., max_length=500)
    http_method: str = Field(..., max_length=10)
    request_ip: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    action: AuditAction
    resource_type: Optional[ResourceType] = None
    resource_id: Optional[str] = Field(None, max_length=100)
    success: bool
    error_message: Optional[str] = Field(None, max_length=1000)
    request_data: Optional[dict] = None
    response_status: Optional[int] = None
    execution_time_ms: Optional[int] = None

class AccessLogCreate(AccessLogBase):
    user_id: Optional[int] = None

class AccessLogResponse(AccessLogBase):
    id: int
    user_id: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# Session Log Schemas
class SessionLogBase(BaseModel):
    user_id: int
    session_token: str = Field(..., max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    expires_at: datetime
    is_active: bool = True

class SessionLogCreate(SessionLogBase):
    pass

class SessionLogUpdate(BaseModel):
    logout_time: Optional[datetime] = None
    is_active: Optional[bool] = None

class SessionLogResponse(SessionLogBase):
    id: int
    login_time: datetime
    logout_time: Optional[datetime] = None

    class Config:
        from_attributes = True

# Permission Check Schemas
class PermissionCheckRequest(BaseModel):
    user_id: int
    resource_type: ResourceType
    permission_type: PermissionType
    resource_id: Optional[str] = None

class PermissionCheckResponse(BaseModel):
    has_permission: bool
    required_permissions: List[str]
    user_permissions: List[str]
    user_roles: List[str]

# Role Assignment Schemas
class AssignRoleRequest(BaseModel):
    user_id: int
    role_id: int
    expires_at: Optional[datetime] = None

class AssignPermissionRequest(BaseModel):
    role_id: int
    permission_id: int
    expires_at: Optional[datetime] = None

# Bulk Operations
class BulkRoleAssignment(BaseModel):
    user_ids: List[int]
    role_id: int
    expires_at: Optional[datetime] = None

class BulkPermissionAssignment(BaseModel):
    role_ids: List[int]
    permission_id: int
    expires_at: Optional[datetime] = None

# Stage Management Schemas
class StageBase(BaseModel):
    stage_type: StageType
    name: str
    description: Optional[str] = None
    is_active: bool = False
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    allowed_roles: List[str] = []
    blocked_endpoints: List[str] = []
    required_permissions: List[str] = []

class StageCreate(StageBase):
    pass

class StageUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    allowed_roles: Optional[List[str]] = None
    blocked_endpoints: Optional[List[str]] = None
    required_permissions: Optional[List[str]] = None

class StageResponse(StageBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True

class StagePermissionBase(BaseModel):
    stage_id: int
    permission_id: int
    is_allowed: bool = True

class StagePermissionCreate(StagePermissionBase):
    pass

class StagePermissionUpdate(BaseModel):
    is_allowed: Optional[bool] = None

class StagePermissionResponse(StagePermissionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CurrentStageResponse(BaseModel):
    current_stage: Optional[StageResponse] = None
    allowed_actions: List[str] = []
    blocked_actions: List[str] = []
    stage_info: dict = {}
    
    class Config:
        from_attributes = True
