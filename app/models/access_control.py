from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy import JSON

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
    STAGE = "stage"

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
    STAGE_CHANGE = "stage_change"

class StageType(str, Enum):
    STAGE_1 = "stage_1"  # College Registration
    STAGE_2 = "stage_2"  # Student Registration
    STAGE_3 = "stage_3"  # Application Processing
    STAGE_4 = "stage_4"  # Results and Allotment
    COMPLETED = "completed"

class Stage(SQLModel, table=True):
    """Stage management table for controlling access based on current stage"""
    id: Optional[int] = Field(default=None, primary_key=True)
    stage_type: StageType = Field(description="Type of stage")
    name: str = Field(max_length=100, description="Stage name")
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=False, description="Whether this stage is currently active")
    start_date: Optional[datetime] = Field(default=None, description="Stage start date")
    end_date: Optional[datetime] = Field(default=None, description="Stage end date")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[int] = Field(default=None, description="Admin who created this stage")
    
    # Stage-specific permissions
    allowed_roles: List[str] = Field(default=[], sa_type=JSON, description="Roles allowed during this stage")
    blocked_endpoints: List[str] = Field(default=[], sa_type=JSON, description="Endpoints blocked during this stage")
    required_permissions: List[str] = Field(default=[], sa_type=JSON, description="Additional permissions required during this stage")
    
    # Relationships
    stage_permissions: List["StagePermission"] = Relationship(back_populates="stage")

class Permission(SQLModel, table=True):
    """Permissions table for granular access control"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=100, description="Permission name")
    description: Optional[str] = Field(default=None, max_length=500)
    resource_type: ResourceType = Field(description="Resource this permission applies to")
    permission_type: PermissionType = Field(description="Type of permission")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    role_permissions: List["RolePermission"] = Relationship(back_populates="permission")
    stage_permissions: List["StagePermission"] = Relationship(back_populates="permission")

class StagePermission(SQLModel, table=True):
    """Permissions specific to stages"""
    id: Optional[int] = Field(default=None, primary_key=True)
    stage_id: int = Field(foreign_key="stage.id")
    permission_id: int = Field(foreign_key="permission.id")
    is_allowed: bool = Field(default=True, description="Whether this permission is allowed during this stage")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    stage: "Stage" = Relationship(back_populates="stage_permissions")
    permission: Permission = Relationship(back_populates="stage_permissions")

class Role(SQLModel, table=True):
    """Roles table for grouping permissions"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=100, description="Role name")
    description: Optional[str] = Field(default=None, max_length=500)
    is_system_role: bool = Field(default=False, description="System-defined role")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    role_permissions: List["RolePermission"] = Relationship(back_populates="role")
    user_roles: List["UserRoleAssignment"] = Relationship(back_populates="role")

class RolePermission(SQLModel, table=True):
    """Many-to-many relationship between roles and permissions"""
    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: int = Field(foreign_key="role.id")
    permission_id: int = Field(foreign_key="permission.id")
    granted_by: Optional[int] = Field(default=None)  # Store as simple integer, not foreign key
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    
    # Relationships
    role: Role = Relationship(back_populates="role_permissions")
    permission: Permission = Relationship(back_populates="role_permissions")
    # Note: granted_by field references user.id but we don't create a relationship to avoid circular imports

class UserRoleAssignment(SQLModel, table=True):
    """Many-to-many relationship between users and roles"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    role_id: int = Field(foreign_key="role.id")
    assigned_by: Optional[int] = Field(default=None)  # Store as simple integer, not foreign key
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    
    # Relationships
    user: "User" = Relationship(back_populates="user_roles")
    role: Role = Relationship(back_populates="user_roles")

class EndpointAccess(SQLModel, table=True):
    """Endpoint access control table"""
    id: Optional[int] = Field(default=None, primary_key=True)
    endpoint_path: str = Field(max_length=500, description="API endpoint path")
    http_method: str = Field(max_length=10, description="HTTP method (GET, POST, etc.)")
    required_permissions: List[str] = Field(default=[], sa_type=JSON, description="Required permissions")
    required_roles: List[str] = Field(default=[], sa_type=JSON, description="Required roles")
    is_public: bool = Field(default=False, description="Public endpoint (no auth required)")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AccessLog(SQLModel, table=True):
    """Audit log for access control"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(foreign_key="user.id", default=None)
    endpoint_path: str = Field(max_length=500)
    http_method: str = Field(max_length=10)
    request_ip: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    action: AuditAction = Field(description="Action performed")
    resource_type: Optional[ResourceType] = Field(default=None)
    resource_id: Optional[str] = Field(default=None, max_length=100)
    success: bool = Field(description="Whether the action was successful")
    error_message: Optional[str] = Field(default=None, max_length=1000)
    request_data: Optional[dict] = Field(default=None, sa_type=JSON)
    response_status: Optional[int] = Field(default=None)
    execution_time_ms: Optional[int] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="access_logs")

class SessionLog(SQLModel, table=True):
    """Session tracking for security"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    session_token: str = Field(max_length=500, description="Session/JWT token")
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    login_time: datetime = Field(default_factory=datetime.utcnow)
    logout_time: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    expires_at: datetime = Field(description="Token expiration time")
    
    # Relationships
    user: "User" = Relationship(back_populates="session_logs")
