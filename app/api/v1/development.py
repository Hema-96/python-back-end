from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Dict, Any
from app.core.database import get_session
from app.middleware.auth import get_current_user
from app.models.user import User, UserRole
from app.models.access_control import (
    Permission, Role, RolePermission, UserRoleAssignment,
    PermissionType, ResourceType
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/development", tags=["Development"])

@router.post("/grant-all-access", summary="Grant all API access to current user (Development only)")
async def grant_all_access(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Grant all API access to the current user based on their role.
    
    **Development Purpose Only**
    
    **Role-based Access:**
    - **Admin**: Gets access to all endpoints and admin functions
    - **College**: Gets access to college-related endpoints and basic user functions
    - **Student**: Gets access to student-related endpoints and basic user functions
    
    **Note:** This is for development/testing purposes only. In production, 
    proper role-based access control should be implemented.
    """
    try:
        # Check if user exists and has a role
        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no role assigned"
            )
        
        user_role = UserRole(current_user.role)
        
        # Get or create necessary roles and permissions
        admin_role = session.exec(select(Role).where(Role.name == "admin")).first()
        college_role = session.exec(select(Role).where(Role.name == "college")).first()
        student_role = session.exec(select(Role).where(Role.name == "student")).first()
        
        # Create roles if they don't exist
        if not admin_role:
            admin_role = Role(
                name="admin",
                description="Administrator role with full access",
                is_active=True
            )
            session.add(admin_role)
            session.commit()
            session.refresh(admin_role)
        
        if not college_role:
            college_role = Role(
                name="college",
                description="College role with college-specific access",
                is_active=True
            )
            session.add(college_role)
            session.commit()
            session.refresh(college_role)
        
        if not student_role:
            student_role = Role(
                name="student",
                description="Student role with student-specific access",
                is_active=True
            )
            session.add(student_role)
            session.commit()
            session.refresh(student_role)
        
        # Get or create all permissions
        all_permissions = session.exec(select(Permission)).all()
        
        if not all_permissions:
            # Create default permissions if none exist
            default_permissions = [
                # User management
                Permission(name="user:read", description="Read user information", resource_type=ResourceType.USER),
                Permission(name="user:write", description="Write user information", resource_type=ResourceType.USER),
                Permission(name="user:delete", description="Delete user", resource_type=ResourceType.USER),
                
                # College management
                Permission(name="college:read", description="Read college information", resource_type=ResourceType.COLLEGE),
                Permission(name="college:write", description="Write college information", resource_type=ResourceType.COLLEGE),
                Permission(name="college:delete", description="Delete college", resource_type=ResourceType.COLLEGE),
                
                # Student management
                Permission(name="student:read", description="Read student information", resource_type=ResourceType.STUDENT),
                Permission(name="student:write", description="Write student information", resource_type=ResourceType.STUDENT),
                Permission(name="student:delete", description="Delete student", resource_type=ResourceType.STUDENT),
                
                # File management
                Permission(name="file:upload", description="Upload files", resource_type=ResourceType.FILE),
                Permission(name="file:download", description="Download files", resource_type=ResourceType.FILE),
                Permission(name="file:delete", description="Delete files", resource_type=ResourceType.FILE),
                
                # System management
                Permission(name="system:admin", description="System administration", resource_type=ResourceType.SYSTEM),
                Permission(name="system:read", description="System read access", resource_type=ResourceType.SYSTEM),
                
                # Stage management
                Permission(name="stage:read", description="Read stage information", resource_type=ResourceType.STAGE),
                Permission(name="stage:write", description="Write stage information", resource_type=ResourceType.STAGE),
                Permission(name="stage:admin", description="Stage administration", resource_type=ResourceType.STAGE),
                
                # Access control
                Permission(name="access:read", description="Read access control", resource_type=ResourceType.ACCESS_CONTROL),
                Permission(name="access:write", description="Write access control", resource_type=ResourceType.ACCESS_CONTROL),
                Permission(name="access:admin", description="Access control administration", resource_type=ResourceType.ACCESS_CONTROL),
            ]
            
            for perm in default_permissions:
                session.add(perm)
            session.commit()
            
            # Refresh permissions list
            all_permissions = session.exec(select(Permission)).all()
        
        # Assign permissions to roles based on user role
        if user_role == UserRole.ADMIN:
            # Admin gets all permissions
            target_role = admin_role
            permissions_to_assign = all_permissions
            
        elif user_role == UserRole.COLLEGE:
            # College gets college-related + basic user permissions
            target_role = college_role
            permissions_to_assign = [
                p for p in all_permissions 
                if any(keyword in p.name.lower() for keyword in [
                    'user:read', 'user:write', 'college', 'file', 'stage:read'
                ])
            ]
            
        elif user_role == UserRole.STUDENT:
            # Student gets student-related + basic user permissions
            target_role = student_role
            permissions_to_assign = [
                p for p in all_permissions 
                if any(keyword in p.name.lower() for keyword in [
                    'user:read', 'user:write', 'student', 'file', 'stage:read'
                ])
            ]
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported user role: {user_role}"
            )
        
        # Clear existing role permissions
        existing_permissions = session.exec(
            select(RolePermission).where(RolePermission.role_id == target_role.id)
        ).all()
        
        for existing_perm in existing_permissions:
            session.delete(existing_perm)
        
        # Assign new permissions to role
        for permission in permissions_to_assign:
            role_permission = RolePermission(
                role_id=target_role.id,
                permission_id=permission.id,
                granted_by=current_user.id
            )
            session.add(role_permission)
        
        # Assign role to user if not already assigned
        existing_user_role = session.exec(
            select(UserRoleAssignment).where(
                UserRoleAssignment.user_id == current_user.id,
                UserRoleAssignment.role_id == target_role.id
            )
        ).first()
        
        if not existing_user_role:
            user_role_assignment = UserRoleAssignment(
                user_id=current_user.id,
                role_id=target_role.id,
                assigned_by=current_user.id
            )
            session.add(user_role_assignment)
        
        session.commit()
        
        # Get assigned permissions for response
        assigned_permissions = session.exec(
            select(Permission)
            .join(RolePermission)
            .where(RolePermission.role_id == target_role.id)
        ).all()
        
        return {
            "message": f"All access granted successfully for {user_role.value} role",
            "user_id": current_user.id,
            "user_email": current_user.email,
            "user_role": user_role.value,
            "assigned_role": target_role.name,
            "assigned_permissions": [
                {
                    "id": perm.id,
                    "name": perm.name,
                    "description": perm.description,
                    "resource_type": perm.resource_type.value
                }
                for perm in assigned_permissions
            ],
            "total_permissions": len(assigned_permissions),
            "development_mode": True,
            "warning": "This is development mode. In production, implement proper RBAC."
        }
        
    except Exception as e:
        logger.error(f"Error granting all access: {e}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error granting all access: {str(e)}"
        )

@router.post("/reset-access", summary="Reset/Revoke all access for current user (Development only)")
async def reset_access(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Reset/Revoke all access for the current user.
    
    **Development Purpose Only**
    
    This will:
    1. Remove all role assignments from the user
    2. Keep the user account but with no permissions
    3. User will need to re-authenticate or get new permissions
    
    **Note:** This is for development/testing purposes only.
    """
    try:
        # Get all user role assignments
        user_role_assignments = session.exec(
            select(UserRoleAssignment).where(UserRoleAssignment.user_id == current_user.id)
        ).all()
        
        # Remove all role assignments
        for assignment in user_role_assignments:
            session.delete(assignment)
        
        session.commit()
        
        return {
            "message": "All access reset successfully",
            "user_id": current_user.id,
            "user_email": current_user.email,
            "removed_roles": len(user_role_assignments),
            "current_status": "No roles assigned - no permissions",
            "development_mode": True,
            "note": "User will need to re-authenticate or get new permissions"
        }
        
    except Exception as e:
        logger.error(f"Error resetting access: {e}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting access: {str(e)}"
        )

@router.get("/current-access", summary="Get current user's access information (Development only)")
async def get_current_access(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get current user's access information including roles and permissions.
    
    **Development Purpose Only**
    
    Returns:
    - User information
    - Assigned roles
    - Permissions for each role
    - Access summary
    """
    try:
        # Get user role assignments
        user_role_assignments = session.exec(
            select(UserRoleAssignment).where(UserRoleAssignment.user_id == current_user.id)
        ).all()
        
        access_info = {
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "role": UserRole(current_user.role).value if current_user.role else None,
                "is_active": current_user.is_active
            },
            "assigned_roles": [],
            "total_permissions": 0,
            "access_summary": "No access"
        }
        
        if user_role_assignments:
            total_permissions = 0
            
            for assignment in user_role_assignments:
                role = session.get(Role, assignment.role_id)
                if role:
                    # Get permissions for this role
                    role_permissions = session.exec(
                        select(Permission)
                        .join(RolePermission)
                        .where(RolePermission.role_id == role.id)
                    ).all()
                    
                    role_info = {
                        "role_id": role.id,
                        "role_name": role.name,
                        "role_description": role.description,
                        "permissions": [
                            {
                                "id": perm.id,
                                "name": perm.name,
                                "description": perm.description,
                                "resource_type": perm.resource_type.value
                            }
                            for perm in role_permissions
                        ],
                        "permission_count": len(role_permissions)
                    }
                    
                    access_info["assigned_roles"].append(role_info)
                    total_permissions += len(role_permissions)
            
            access_info["total_permissions"] = total_permissions
            
            if total_permissions > 0:
                access_info["access_summary"] = f"Has access to {total_permissions} permissions across {len(user_role_assignments)} roles"
            else:
                access_info["access_summary"] = "Roles assigned but no permissions"
        
        access_info["development_mode"] = True
        access_info["warning"] = "This is development mode. In production, implement proper RBAC."
        
        return access_info
        
    except Exception as e:
        logger.error(f"Error getting current access: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting current access: {str(e)}"
        )
