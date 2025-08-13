from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_session
from app.services.access_control_service import AccessControlService
from app.schemas.access_control import (
    PermissionCreate, PermissionUpdate, PermissionResponse,
    RoleCreate, RoleUpdate, RoleResponse,
    RolePermissionCreate, RolePermissionResponse,
    UserRoleAssignmentCreate, UserRoleAssignmentResponse,
    EndpointAccessCreate, EndpointAccessResponse,
    AccessLogResponse, SessionLogResponse,
    PermissionCheckRequest, PermissionCheckResponse,
    AssignRoleRequest, AssignPermissionRequest,
    BulkRoleAssignment, BulkPermissionAssignment
)
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.access_control import ResourceType, PermissionType, AuditAction
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/access-control", tags=["Access Control"])

# Permission Management Endpoints
@router.post("/permissions", response_model=PermissionResponse, summary="Create a new permission")
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new permission. Requires system_admin permission."""
    access_service = AccessControlService(session)
    
    # Check if user has permission to create permissions
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create permissions"
        )
    
    return access_service.create_permission(permission_data, current_user.id)

@router.get("/permissions", response_model=List[PermissionResponse], summary="Get all permissions")
async def get_permissions(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all permissions. Requires system_read permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view permissions"
        )
    
    return access_service.get_permissions(skip, limit, active_only)

@router.get("/permissions/{permission_id}", response_model=PermissionResponse, summary="Get permission by ID")
async def get_permission(
    permission_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get permission by ID. Requires system_read permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view permissions"
        )
    
    permission = access_service.get_permission_by_id(permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return permission

@router.put("/permissions/{permission_id}", response_model=PermissionResponse, summary="Update permission")
async def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update permission. Requires system_admin permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update permissions"
        )
    
    return access_service.update_permission(permission_id, permission_data)

# Role Management Endpoints
@router.post("/roles", response_model=RoleResponse, summary="Create a new role")
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new role. Requires system_admin permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create roles"
        )
    
    return access_service.create_role(role_data, current_user.id)

@router.get("/roles", response_model=List[RoleResponse], summary="Get all roles")
async def get_roles(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all roles. Requires system_read permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view roles"
        )
    
    return access_service.get_roles(skip, limit, active_only)

@router.get("/roles/{role_id}", response_model=RoleResponse, summary="Get role by ID")
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get role by ID. Requires system_read permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view roles"
        )
    
    role = access_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return role

@router.put("/roles/{role_id}", response_model=RoleResponse, summary="Update role")
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update role. Requires system_admin permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update roles"
        )
    
    return access_service.update_role(role_id, role_data)

# Role-Permission Management Endpoints
@router.post("/roles/{role_id}/permissions", response_model=RolePermissionResponse, summary="Assign permission to role")
async def assign_permission_to_role(
    role_id: int,
    permission_data: AssignPermissionRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Assign permission to role. Requires system_admin permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to assign permissions"
        )
    
    return access_service.assign_permission_to_role(
        role_id, 
        permission_data.permission_id, 
        current_user.id, 
        permission_data.expires_at
    )

@router.delete("/roles/{role_id}/permissions/{permission_id}", summary="Remove permission from role")
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Remove permission from role. Requires system_admin permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to remove permissions"
        )
    
    success = access_service.remove_permission_from_role(role_id, permission_id)
    if success:
        return {"message": "Permission removed from role successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove permission from role"
        )

# User-Role Management Endpoints
@router.post("/users/{user_id}/roles", response_model=UserRoleAssignmentResponse, summary="Assign role to user")
async def assign_role_to_user(
    user_id: int,
    role_data: AssignRoleRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Assign role to user. Requires user_admin permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.USER, PermissionType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to assign roles"
        )
    
    return access_service.assign_role_to_user(
        user_id, 
        role_data.role_id, 
        current_user.id, 
        role_data.expires_at
    )

@router.delete("/users/{user_id}/roles/{role_id}", summary="Remove role from user")
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Remove role from user. Requires user_admin permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.USER, PermissionType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to remove roles"
        )
    
    success = access_service.remove_role_from_user(user_id, role_id)
    if success:
        return {"message": "Role removed from user successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove role from user"
        )

# Bulk Operations
@router.post("/users/bulk-assign-role", summary="Bulk assign role to users")
async def bulk_assign_role(
    bulk_data: BulkRoleAssignment,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Bulk assign role to multiple users. Requires user_admin permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.USER, PermissionType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to assign roles"
        )
    
    results = []
    for user_id in bulk_data.user_ids:
        try:
            user_role = access_service.assign_role_to_user(
                user_id, 
                bulk_data.role_id, 
                current_user.id, 
                bulk_data.expires_at
            )
            results.append({"user_id": user_id, "success": True, "user_role_id": user_role.id})
        except Exception as e:
            results.append({"user_id": user_id, "success": False, "error": str(e)})
    
    return {"results": results}

@router.post("/roles/bulk-assign-permission", summary="Bulk assign permission to roles")
async def bulk_assign_permission(
    bulk_data: BulkPermissionAssignment,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Bulk assign permission to multiple roles. Requires system_admin permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to assign permissions"
        )
    
    results = []
    for role_id in bulk_data.role_ids:
        try:
            role_permission = access_service.assign_permission_to_role(
                role_id, 
                bulk_data.permission_id, 
                current_user.id, 
                bulk_data.expires_at
            )
            results.append({"role_id": role_id, "success": True, "role_permission_id": role_permission.id})
        except Exception as e:
            results.append({"role_id": role_id, "success": False, "error": str(e)})
    
    return {"results": results}

# Permission Checking Endpoints
@router.post("/check-permission", response_model=PermissionCheckResponse, summary="Check user permission")
async def check_permission(
    permission_check: PermissionCheckRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Check if user has specific permission. Requires system_read permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to check permissions"
        )
    
    has_permission = access_service.check_permission(
        permission_check.user_id,
        permission_check.resource_type,
        permission_check.permission_type,
        permission_check.resource_id
    )
    
    user_permissions = list(access_service.get_user_permissions(permission_check.user_id))
    user_roles = list(access_service.get_user_roles(permission_check.user_id))
    
    required_permissions = [
        f"{permission_check.resource_type.value}_{permission_check.permission_type.value}",
        f"{permission_check.resource_type.value}_admin"
    ]
    
    return PermissionCheckResponse(
        has_permission=has_permission,
        required_permissions=required_permissions,
        user_permissions=user_permissions,
        user_roles=user_roles
    )

@router.get("/users/{user_id}/permissions", summary="Get user permissions")
async def get_user_permissions(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all permissions for a user. Requires system_read permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view user permissions"
        )
    
    permissions = list(access_service.get_user_permissions(user_id))
    roles = list(access_service.get_user_roles(user_id))
    
    return {
        "user_id": user_id,
        "permissions": permissions,
        "roles": roles
    }

# Endpoint Access Control
@router.post("/endpoints", response_model=EndpointAccessResponse, summary="Create endpoint access rule")
async def create_endpoint_access(
    endpoint_data: EndpointAccessCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create endpoint access rule. Requires system_admin permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create endpoint rules"
        )
    
    # This would need to be implemented in the service
    # For now, return a placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint access control not yet implemented"
    )

# Audit Logging Endpoints
@router.get("/audit-logs", response_model=List[AccessLogResponse], summary="Get audit logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action: Optional[AuditAction] = None,
    resource_type: Optional[ResourceType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get audit logs. Requires system_read permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view audit logs"
        )
    
    # This would need to be implemented in the service
    # For now, return a placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Audit log retrieval not yet implemented"
    )

@router.get("/session-logs", response_model=List[SessionLogResponse], summary="Get session logs")
async def get_session_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get session logs. Requires system_read permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view session logs"
        )
    
    # This would need to be implemented in the service
    # For now, return a placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Session log retrieval not yet implemented"
    )

# System Management Endpoints
@router.post("/initialize", summary="Initialize default permissions and roles")
async def initialize_system(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Initialize default permissions and roles. Requires system_admin permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to initialize system"
        )
    
    try:
        # Check current state
        permissions_count = len(access_service.get_permissions(limit=1000))
        roles_count = len(access_service.get_roles(limit=1000))
        
        # Initialize if needed
        access_service.initialize_default_permissions()
        access_service.initialize_default_roles()
        
        # Get updated counts
        new_permissions_count = len(access_service.get_permissions(limit=1000))
        new_roles_count = len(access_service.get_roles(limit=1000))
        
        permissions_added = new_permissions_count - permissions_count
        roles_added = new_roles_count - roles_count
        
        return {
            "message": "System initialization completed",
            "permissions_created": permissions_added > 0,
            "roles_created": roles_added > 0,
            "permissions_added": permissions_added,
            "roles_added": roles_added,
            "total_permissions": new_permissions_count,
            "total_roles": new_roles_count
        }
    except Exception as e:
        logger.error(f"Error initializing system: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize system"
        )

@router.get("/health", summary="Access control system health check")
async def access_control_health(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Check access control system health. Requires system_read permission."""
    access_service = AccessControlService(session)
    
    if not access_service.check_permission(current_user.id, ResourceType.SYSTEM, PermissionType.READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to check system health"
        )
    
    try:
        permissions_count = len(access_service.get_permissions(limit=1000))
        roles_count = len(access_service.get_roles(limit=1000))
        
        return {
            "status": "healthy",
            "permissions_count": permissions_count,
            "roles_count": roles_count,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error checking access control health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Access control system unhealthy"
        )
