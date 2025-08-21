from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from app.core.database import get_session
from app.services.stage_service import StageService
from app.models.user import UserRole
import logging

logger = logging.getLogger(__name__)

async def stage_access_middleware(request: Request, call_next):
    """
    Middleware to check stage-based access controls for endpoints.
    
    This middleware intercepts requests and checks if the current stage
    allows access to the requested endpoint based on the user's role.
    """
    try:
        # Skip stage checks for certain endpoints
        skip_paths = [
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/api/stages/current",
            "/api/stages/check-registration",
            "/api/auth/login",
            "/api/auth/refresh",
            "/api/auth/verify-email-otp"
        ]
        
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Get current stage information
        session = next(get_session())
        stage_service = StageService(session)
        
        # Check if endpoint is blocked in current stage
        current_stage = stage_service.get_current_stage()
        if current_stage:
            if request.url.path in current_stage.blocked_endpoints:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "message": "Endpoint blocked in current stage",
                        "current_stage": current_stage.name,
                        "description": current_stage.description,
                        "blocked_endpoints": current_stage.blocked_endpoints
                    }
                )
        
        # Continue with the request
        response = await call_next(request)
        return response
        
    except Exception as e:
        logger.error(f"Stage middleware error: {e}")
        # Continue with the request even if stage check fails
        return await call_next(request)
    finally:
        if 'session' in locals():
            session.close()

def require_stage_permission(allowed_stages: list):
    """
    Dependency to require specific stage permissions for endpoints.
    
    Args:
        allowed_stages: List of stage types that are allowed to access this endpoint
    """
    def stage_permission_checker(request: Request):
        try:
            session = next(get_session())
            stage_service = StageService(session)
            current_stage = stage_service.get_current_stage()
            
            if not current_stage:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No active stage found"
                )
            
            if current_stage.stage_type not in allowed_stages:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "message": f"Endpoint not available in current stage: {current_stage.name}",
                        "current_stage": current_stage.stage_type,
                        "allowed_stages": allowed_stages,
                        "description": current_stage.description
                    }
                )
            
            return current_stage
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Stage permission check error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error checking stage permissions"
            )
        finally:
            if 'session' in locals():
                session.close()
    
    return stage_permission_checker

def require_college_registration_stage():
    """Dependency to require Stage 1 (College Registration) for college-related endpoints"""
    return require_stage_permission(["stage_1"])

def require_student_registration_stage():
    """Dependency to require Stage 2 (Student Registration) for student-related endpoints"""
    return require_stage_permission(["stage_2"])

def require_application_processing_stage():
    """Dependency to require Stage 3 (Application Processing) for processing endpoints"""
    return require_stage_permission(["stage_3"])

def require_results_stage():
    """Dependency to require Stage 4 (Results) for results-related endpoints"""
    return require_stage_permission(["stage_4"])

def require_any_active_stage():
    """Dependency to require any active stage (not completed)"""
    return require_stage_permission(["stage_1", "stage_2", "stage_3", "stage_4"])
