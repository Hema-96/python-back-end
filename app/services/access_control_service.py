from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Set
from app.models.access_control import (
    Permission, Role, RolePermission, UserRoleAssignment, EndpointAccess, 
    AccessLog, SessionLog, PermissionType, ResourceType, AuditAction
)
from app.models.user import User, UserRole as UserRoleEnum
from app.schemas.access_control import (
    PermissionCreate, PermissionUpdate, RoleCreate, RoleUpdate,
    RolePermissionCreate, UserRoleAssignmentCreate, EndpointAccessCreate,
    AccessLogCreate, SessionLogCreate, PermissionCheckRequest
)
import logging
import time
from fastapi import Request

logger = logging.getLogger(__name__)

class AccessControlService:
    def __init__(self, session: Session):
        self.session = session

    # Permission Management
    def create_permission(self, permission_data: PermissionCreate, created_by: int) -> Permission:
        """Create a new permission"""
        try:
            # Check if permission already exists
            existing = self.session.exec(
                select(Permission).where(Permission.name == permission_data.name)
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Permission already exists"
                )

            permission = Permission(
                name=permission_data.name,
                description=permission_data.description,
                resource_type=permission_data.resource_type,
                permission_type=permission_data.permission_type,
                is_active=permission_data.is_active
            )
            
            self.session.add(permission)
            self.session.commit()
            self.session.refresh(permission)
            
            logger.info(f"Permission created: {permission.name} by user {created_by}")
            return permission
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating permission: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def get_permissions(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Permission]:
        """Get all permissions with optional filtering"""
        try:
            query = select(Permission)
            if active_only:
                query = query.where(Permission.is_active == True)
            
            permissions = self.session.exec(query.offset(skip).limit(limit)).all()
            return permissions
            
        except Exception as e:
            logger.error(f"Error fetching permissions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def get_permission_by_id(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID"""
        return self.session.exec(
            select(Permission).where(Permission.id == permission_id)
        ).first()

    def update_permission(self, permission_id: int, permission_data: PermissionUpdate) -> Permission:
        """Update permission"""
        try:
            permission = self.get_permission_by_id(permission_id)
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Permission not found"
                )

            update_data = permission_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(permission, field, value)
            
            permission.updated_at = datetime.utcnow()
            self.session.add(permission)
            self.session.commit()
            self.session.refresh(permission)
            
            return permission
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating permission: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    # Role Management
    def create_role(self, role_data: RoleCreate, created_by: int) -> Role:
        """Create a new role"""
        try:
            existing = self.session.exec(
                select(Role).where(Role.name == role_data.name)
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role already exists"
                )

            role = Role(
                name=role_data.name,
                description=role_data.description,
                is_system_role=role_data.is_system_role,
                is_active=role_data.is_active
            )
            
            self.session.add(role)
            self.session.commit()
            self.session.refresh(role)
            
            logger.info(f"Role created: {role.name} by user {created_by}")
            return role
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating role: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def get_roles(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Role]:
        """Get all roles with optional filtering"""
        try:
            query = select(Role)
            if active_only:
                query = query.where(Role.is_active == True)
            
            roles = self.session.exec(query.offset(skip).limit(limit)).all()
            return roles
            
        except Exception as e:
            logger.error(f"Error fetching roles: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        return self.session.exec(
            select(Role).where(Role.id == role_id)
        ).first()

    def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        """Update role"""
        try:
            role = self.get_role_by_id(role_id)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role not found"
                )

            update_data = role_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(role, field, value)
            
            role.updated_at = datetime.utcnow()
            self.session.add(role)
            self.session.commit()
            self.session.refresh(role)
            
            return role
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating role: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    # Role-Permission Management
    def assign_permission_to_role(self, role_id: int, permission_id: int, granted_by: int, expires_at: Optional[datetime] = None) -> RolePermission:
        """Assign permission to role"""
        try:
            # Check if role and permission exist
            role = self.get_role_by_id(role_id)
            permission = self.get_permission_by_id(permission_id)
            
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role not found"
                )
            
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Permission not found"
                )

            # Check if assignment already exists
            existing = self.session.exec(
                select(RolePermission).where(
                    and_(
                        RolePermission.role_id == role_id,
                        RolePermission.permission_id == permission_id,
                        RolePermission.is_active == True
                    )
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Permission already assigned to role"
                )

            role_permission = RolePermission(
                role_id=role_id,
                permission_id=permission_id,
                granted_by=granted_by,
                expires_at=expires_at
            )
            
            self.session.add(role_permission)
            self.session.commit()
            self.session.refresh(role_permission)
            
            logger.info(f"Permission {permission.name} assigned to role {role.name} by user {granted_by}")
            return role_permission
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error assigning permission to role: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def remove_permission_from_role(self, role_id: int, permission_id: int) -> bool:
        """Remove permission from role"""
        try:
            role_permission = self.session.exec(
                select(RolePermission).where(
                    and_(
                        RolePermission.role_id == role_id,
                        RolePermission.permission_id == permission_id,
                        RolePermission.is_active == True
                    )
                )
            ).first()
            
            if not role_permission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role-permission assignment not found"
                )

            role_permission.is_active = False
            self.session.add(role_permission)
            self.session.commit()
            
            logger.info(f"Permission {permission_id} removed from role {role_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing permission from role: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    # User-Role Management
    def assign_role_to_user(self, user_id: int, role_id: int, assigned_by: int, expires_at: Optional[datetime] = None) -> UserRoleAssignment:
        """Assign role to user"""
        try:
            # Check if user and role exist
            user = self.session.exec(select(User).where(User.id == user_id)).first()
            role = self.get_role_by_id(role_id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role not found"
                )

            # Check if assignment already exists
            existing = self.session.exec(
                select(UserRoleAssignment).where(
                    and_(
                        UserRoleAssignment.user_id == user_id,
                        UserRoleAssignment.role_id == role_id,
                        UserRoleAssignment.is_active == True
                    )
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role already assigned to user"
                )

            user_role = UserRoleAssignment(
                user_id=user_id,
                role_id=role_id,
                assigned_by=assigned_by,
                expires_at=expires_at
            )
            
            self.session.add(user_role)
            self.session.commit()
            self.session.refresh(user_role)
            
            logger.info(f"Role {role.name} assigned to user {user.email} by user {assigned_by}")
            return user_role
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error assigning role to user: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def remove_role_from_user(self, user_id: int, role_id: int) -> bool:
        """Remove role from user"""
        try:
            user_role = self.session.exec(
                select(UserRoleAssignment).where(
                    and_(
                        UserRoleAssignment.user_id == user_id,
                        UserRoleAssignment.role_id == role_id,
                        UserRoleAssignment.is_active == True
                    )
                )
            ).first()
            
            if not user_role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User-role assignment not found"
                )

            user_role.is_active = False
            self.session.add(user_role)
            self.session.commit()
            
            logger.info(f"Role {role_id} removed from user {user_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing role from user: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    # Permission Checking
    def get_user_permissions(self, user_id: int) -> Set[str]:
        """Get all permissions for a user"""
        try:
            # Get user's active roles
            user_roles = self.session.exec(
                select(UserRoleAssignment).where(
                    and_(
                        UserRoleAssignment.user_id == user_id,
                        UserRoleAssignment.is_active == True,
                        or_(
                            UserRoleAssignment.expires_at == None,
                            UserRoleAssignment.expires_at > datetime.utcnow()
                        )
                    )
                )
            ).all()
            
            if not user_roles:
                return set()

            role_ids = [ur.role_id for ur in user_roles]
            
            # Get permissions for these roles
            role_permissions = self.session.exec(
                select(RolePermission).where(
                    and_(
                        RolePermission.role_id.in_(role_ids),
                        RolePermission.is_active == True,
                        or_(
                            RolePermission.expires_at == None,
                            RolePermission.expires_at > datetime.utcnow()
                        )
                    )
                )
            ).all()
            
            if not role_permissions:
                return set()

            permission_ids = [rp.permission_id for rp in role_permissions]
            
            # Get permission names
            permissions = self.session.exec(
                select(Permission).where(
                    and_(
                        Permission.id.in_(permission_ids),
                        Permission.is_active == True
                    )
                )
            ).all()
            
            return {p.name for p in permissions}
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return set()

    def get_user_roles(self, user_id: int) -> Set[str]:
        """Get all roles for a user"""
        try:
            user_roles = self.session.exec(
                select(UserRoleAssignment).where(
                    and_(
                        UserRoleAssignment.user_id == user_id,
                        UserRoleAssignment.is_active == True,
                        or_(
                            UserRoleAssignment.expires_at == None,
                            UserRoleAssignment.expires_at > datetime.utcnow()
                        )
                    )
                )
            ).all()
            
            if not user_roles:
                return set()

            role_ids = [ur.role_id for ur in user_roles]
            
            roles = self.session.exec(
                select(Role).where(
                    and_(
                        Role.id.in_(role_ids),
                        Role.is_active == True
                    )
                )
            ).all()
            
            return {r.name for r in roles}
            
        except Exception as e:
            logger.error(f"Error getting user roles: {e}")
            return set()

    def check_permission(self, user_id: int, resource_type: ResourceType, permission_type: PermissionType, resource_id: Optional[str] = None) -> bool:
        """Check if user has specific permission"""
        try:
            user_permissions = self.get_user_permissions(user_id)
            
            # Check for specific permission
            specific_permission = f"{resource_type.value}_{permission_type.value}"
            if resource_id:
                specific_permission = f"{resource_type.value}_{permission_type.value}_{resource_id}"
            
            if specific_permission in user_permissions:
                return True
            
            # Check for general permission
            general_permission = f"{resource_type.value}_{permission_type.value}"
            if general_permission in user_permissions:
                return True
            
            # Check for admin permission
            admin_permission = f"{resource_type.value}_admin"
            if admin_permission in user_permissions:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False

    # Endpoint Access Control
    def check_endpoint_access(self, user_id: int, endpoint_path: str, http_method: str) -> bool:
        """Check if user has access to specific endpoint"""
        try:
            # Get endpoint access rules
            endpoint_access = self.session.exec(
                select(EndpointAccess).where(
                    and_(
                        EndpointAccess.endpoint_path == endpoint_path,
                        EndpointAccess.http_method == http_method.upper(),
                        EndpointAccess.is_active == True
                    )
                )
            ).first()
            
            if not endpoint_access:
                # No specific rule found, allow access
                return True
            
            if endpoint_access.is_public:
                return True
            
            user_permissions = self.get_user_permissions(user_id)
            user_roles = self.get_user_roles(user_id)
            
            # Check required permissions
            if endpoint_access.required_permissions:
                has_permission = any(perm in user_permissions for perm in endpoint_access.required_permissions)
                if not has_permission:
                    return False
            
            # Check required roles
            if endpoint_access.required_roles:
                has_role = any(role in user_roles for role in endpoint_access.required_roles)
                if not has_role:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking endpoint access: {e}")
            return False

    # Audit Logging
    def log_access(self, access_data: AccessLogCreate) -> AccessLog:
        """Log access attempt"""
        try:
            access_log = AccessLog(
                user_id=access_data.user_id,
                endpoint_path=access_data.endpoint_path,
                http_method=access_data.http_method,
                request_ip=access_data.request_ip,
                user_agent=access_data.user_agent,
                action=access_data.action,
                resource_type=access_data.resource_type,
                resource_id=access_data.resource_id,
                success=access_data.success,
                error_message=access_data.error_message,
                request_data=access_data.request_data,
                response_status=access_data.response_status,
                execution_time_ms=access_data.execution_time_ms
            )
            
            self.session.add(access_log)
            self.session.commit()
            self.session.refresh(access_log)
            
            return access_log
            
        except Exception as e:
            logger.error(f"Error logging access: {e}")
            self.session.rollback()
            return None

    def log_session(self, session_data: SessionLogCreate) -> SessionLog:
        """Log session activity"""
        try:
            session_log = SessionLog(
                user_id=session_data.user_id,
                session_token=session_data.session_token,
                ip_address=session_data.ip_address,
                user_agent=session_data.user_agent,
                expires_at=session_data.expires_at,
                is_active=session_data.is_active
            )
            
            self.session.add(session_log)
            self.session.commit()
            self.session.refresh(session_log)
            
            return session_log
            
        except Exception as e:
            logger.error(f"Error logging session: {e}")
            self.session.rollback()
            return None

    def update_session_logout(self, session_token: str) -> bool:
        """Update session logout time"""
        try:
            session_log = self.session.exec(
                select(SessionLog).where(
                    and_(
                        SessionLog.session_token == session_token,
                        SessionLog.is_active == True
                    )
                )
            ).first()
            
            if session_log:
                session_log.logout_time = datetime.utcnow()
                session_log.is_active = False
                self.session.add(session_log)
                self.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating session logout: {e}")
            self.session.rollback()
            return False

    # Initialize Default Data
    def initialize_default_permissions(self) -> None:
        """Initialize default permissions"""
        try:
            # Check if permissions already exist
            existing_count = len(self.session.exec(select(Permission)).all())
            if existing_count > 0:
                logger.info(f"Permissions already exist ({existing_count} found), skipping initialization")
                return
            
            default_permissions = [
                # User permissions
                {"name": "user_read", "description": "Read user data", "resource_type": ResourceType.USER, "permission_type": PermissionType.READ},
                {"name": "user_write", "description": "Create/update user data", "resource_type": ResourceType.USER, "permission_type": PermissionType.WRITE},
                {"name": "user_delete", "description": "Delete user data", "resource_type": ResourceType.USER, "permission_type": PermissionType.DELETE},
                {"name": "user_admin", "description": "Full user administration", "resource_type": ResourceType.USER, "permission_type": PermissionType.ADMIN},
                
                # College permissions
                {"name": "college_read", "description": "Read college data", "resource_type": ResourceType.COLLEGE, "permission_type": PermissionType.READ},
                {"name": "college_write", "description": "Create/update college data", "resource_type": ResourceType.COLLEGE, "permission_type": PermissionType.WRITE},
                {"name": "college_approve", "description": "Approve college data", "resource_type": ResourceType.COLLEGE, "permission_type": PermissionType.APPROVE},
                {"name": "college_verify", "description": "Verify college data", "resource_type": ResourceType.COLLEGE, "permission_type": PermissionType.VERIFY},
                {"name": "college_admin", "description": "Full college administration", "resource_type": ResourceType.COLLEGE, "permission_type": PermissionType.ADMIN},
                
                # Student permissions
                {"name": "student_read", "description": "Read student data", "resource_type": ResourceType.STUDENT, "permission_type": PermissionType.READ},
                {"name": "student_write", "description": "Create/update student data", "resource_type": ResourceType.STUDENT, "permission_type": PermissionType.WRITE},
                {"name": "student_verify", "description": "Verify student data", "resource_type": ResourceType.STUDENT, "permission_type": PermissionType.VERIFY},
                {"name": "student_admin", "description": "Full student administration", "resource_type": ResourceType.STUDENT, "permission_type": PermissionType.ADMIN},
                
                # System permissions
                {"name": "system_admin", "description": "Full system administration", "resource_type": ResourceType.SYSTEM, "permission_type": PermissionType.ADMIN},
                {"name": "system_read", "description": "Read system data", "resource_type": ResourceType.SYSTEM, "permission_type": PermissionType.READ},
            ]
            
            permissions_created = 0
            for perm_data in default_permissions:
                existing = self.session.exec(
                    select(Permission).where(Permission.name == perm_data["name"])
                ).first()
                
                if not existing:
                    permission = Permission(**perm_data)
                    self.session.add(permission)
                    permissions_created += 1
            
            if permissions_created > 0:
                self.session.commit()
                logger.info(f"Default permissions initialized: {permissions_created} permissions created")
            else:
                logger.info("No new permissions needed to be created")
            
        except Exception as e:
            logger.error(f"Error initializing default permissions: {e}")
            self.session.rollback()
            raise

    def initialize_default_roles(self) -> None:
        """Initialize default roles"""
        try:
            # Check if roles already exist
            existing_count = len(self.session.exec(select(Role)).all())
            if existing_count > 0:
                logger.info(f"Roles already exist ({existing_count} found), skipping initialization")
                return
            
            default_roles = [
                {"name": "super_admin", "description": "Super Administrator with full access", "is_system_role": True},
                {"name": "admin", "description": "Administrator with management access", "is_system_role": True},
                {"name": "college_admin", "description": "College Administrator", "is_system_role": True},
                {"name": "student", "description": "Student user", "is_system_role": True},
                {"name": "viewer", "description": "Read-only user", "is_system_role": True},
            ]
            
            roles_created = 0
            for role_data in default_roles:
                existing = self.session.exec(
                    select(Role).where(Role.name == role_data["name"])
                ).first()
                
                if not existing:
                    role = Role(**role_data)
                    self.session.add(role)
                    roles_created += 1
            
            if roles_created > 0:
                self.session.commit()
                logger.info(f"Default roles initialized: {roles_created} roles created")
            else:
                logger.info("No new roles needed to be created")
            
        except Exception as e:
            logger.error(f"Error initializing default roles: {e}")
            self.session.rollback()
            raise
