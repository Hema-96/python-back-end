from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing import Optional, Callable
from datetime import datetime
import time
import logging
from app.core.database import get_session
from app.services.access_control_service import AccessControlService
from app.models.access_control import ResourceType, PermissionType, AuditAction
from app.schemas.access_control import AccessLogCreate
from app.core.security import verify_token

logger = logging.getLogger(__name__)

class AccessControlMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Skip access control for certain paths
            if self._should_skip_access_control(request.url.path):
                await self.app(scope, receive, send)
                return

            # Get session for database operations
            session = next(get_session())
            access_service = AccessControlService(session)
            
            start_time = time.time()
            success = True
            error_message = None
            response_status = None
            
            try:
                # Extract user from token
                user_id = await self._get_user_from_request(request, session)
                
                # Check endpoint access
                if user_id:
                    has_access = access_service.check_endpoint_access(
                        user_id, 
                        request.url.path, 
                        request.method
                    )
                    
                    if not has_access:
                        success = False
                        error_message = "Access denied"
                        response_status = 403
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Access denied"
                        )
                
                # Process the request
                await self.app(scope, receive, send)
                
                # Get response status
                if hasattr(scope, 'response_status'):
                    response_status = scope.response_status
                
            except HTTPException as e:
                success = False
                error_message = str(e.detail)
                response_status = e.status_code
                raise
            except Exception as e:
                success = False
                error_message = str(e)
                response_status = 500
                raise
            finally:
                # Calculate execution time
                execution_time = int((time.time() - start_time) * 1000)
                
                # Log access attempt
                try:
                    user_id = await self._get_user_from_request(request, session)
                    
                    # Determine action based on HTTP method
                    action = self._get_action_from_method(request.method)
                    
                    # Determine resource type from path
                    resource_type = self._get_resource_type_from_path(request.url.path)
                    
                    access_data = AccessLogCreate(
                        user_id=user_id,
                        endpoint_path=request.url.path,
                        http_method=request.method,
                        request_ip=self._get_client_ip(request),
                        user_agent=request.headers.get("user-agent"),
                        action=action,
                        resource_type=resource_type,
                        resource_id=None,  # Could be extracted from path parameters
                        success=success,
                        error_message=error_message,
                        request_data=None,  # Could include request body for debugging
                        response_status=response_status,
                        execution_time_ms=execution_time
                    )
                    
                    access_service.log_access(access_data)
                    
                except Exception as e:
                    logger.error(f"Error logging access: {e}")
                
                session.close()

    def _should_skip_access_control(self, path: str) -> bool:
        """Check if access control should be skipped for this path"""
        skip_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/send-email-otp",
            "/api/auth/verify-email-otp",
            "/api/auth/password-reset",
            "/api/auth/set-new-password"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)

    async def _get_user_from_request(self, request: Request, session: Session) -> Optional[int]:
        """Extract user ID from request token"""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            payload = verify_token(token)
            
            if payload and "sub" in payload:
                return int(payload["sub"])
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting user from request: {e}")
            return None

    def _get_action_from_method(self, method: str) -> AuditAction:
        """Map HTTP method to audit action"""
        method_actions = {
            "GET": AuditAction.READ,
            "POST": AuditAction.CREATE,
            "PUT": AuditAction.UPDATE,
            "PATCH": AuditAction.UPDATE,
            "DELETE": AuditAction.DELETE
        }
        return method_actions.get(method.upper(), AuditAction.READ)

    def _get_resource_type_from_path(self, path: str) -> Optional[ResourceType]:
        """Extract resource type from API path"""
        if "/api/users" in path:
            return ResourceType.USER
        elif "/api/colleges" in path:
            return ResourceType.COLLEGE
        elif "/api/students" in path:
            return ResourceType.STUDENT
        elif "/api/admin" in path:
            return ResourceType.ADMIN
        elif "/api/auth" in path:
            return ResourceType.AUTH
        elif "/api/access-control" in path:
            return ResourceType.SYSTEM
        else:
            return None

    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Get client IP address"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to client host
        return request.client.host if request.client else None

def require_permission(resource_type: ResourceType, permission_type: PermissionType):
    """Decorator to require specific permission for endpoint"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # This would be implemented to check permissions
            # For now, it's a placeholder
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role_name: str):
    """Decorator to require specific role for endpoint"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # This would be implemented to check roles
            # For now, it's a placeholder
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def log_access(action: AuditAction, resource_type: Optional[ResourceType] = None):
    """Decorator to log access to endpoint"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # This would be implemented to log access
            # For now, it's a placeholder
            return await func(*args, **kwargs)
        return wrapper
    return decorator
