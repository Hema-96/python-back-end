from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from app.core.database import get_session
from app.services.stage_service import StageService
from app.schemas.access_control import (
    StageCreate, StageUpdate, StageResponse, 
    StagePermissionCreate, CurrentStageResponse
)
from app.middleware.auth import get_current_user, require_admin
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stages", tags=["Stages"])

@router.post("/", response_model=StageResponse, summary="Create a new stage")
async def create_stage(
    stage_data: StageCreate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Create a new stage for controlling access based on current phase.
    
    **Required Role:** Admin
    
    This endpoint allows admins to create new stages with specific permissions
    and access controls for different phases of the application.
    """
    try:
        stage_service = StageService(session)
        return stage_service.create_stage(stage_data, current_user.id)
    except Exception as e:
        logger.error(f"Stage creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating stage: {str(e)}"
        )

@router.get("/", response_model=List[StageResponse], summary="Get all stages")
async def get_all_stages(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get all stages in the system.
    
    **Required Role:** Admin
    """
    try:
        stage_service = StageService(session)
        return stage_service.get_all_stages()
    except Exception as e:
        logger.error(f"Error getting all stages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving stages: {str(e)}"
        )

@router.get("/current", response_model=CurrentStageResponse, summary="Get current stage information")
async def get_current_stage_info(
    session: Session = Depends(get_session)
):
    """
    Get information about the currently active stage.
    
    **Public endpoint** - No authentication required.
    
    Returns comprehensive information about the current stage including:
    - Current stage details
    - Allowed actions
    - Blocked actions
    - Stage-specific information
    """
    try:
        stage_service = StageService(session)
        return stage_service.get_stage_info()
    except Exception as e:
        logger.error(f"Error getting current stage info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving current stage: {str(e)}"
        )

@router.put("/{stage_id}", response_model=StageResponse, summary="Update a stage")
async def update_stage(
    stage_id: int,
    stage_data: StageUpdate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Update an existing stage.
    
    **Required Role:** Admin
    """
    try:
        stage_service = StageService(session)
        return stage_service.update_stage(stage_id, stage_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Stage update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating stage: {str(e)}"
        )

@router.post("/{stage_id}/activate", response_model=StageResponse, summary="Activate a stage")
async def activate_stage(
    stage_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Activate a specific stage and deactivate all others.
    
    **Required Role:** Admin
    
    This will automatically deactivate all other stages and activate the specified one.
    """
    try:
        stage_service = StageService(session)
        return stage_service.activate_stage(stage_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Stage activation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activating stage: {str(e)}"
        )

@router.post("/{stage_id}/deactivate", response_model=StageResponse, summary="Deactivate a stage")
async def deactivate_stage(
    stage_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Deactivate a specific stage.
    
    **Required Role:** Admin
    """
    try:
        stage_service = StageService(session)
        return stage_service.deactivate_stage(stage_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Stage deactivation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating stage: {str(e)}"
        )

@router.post("/initialize", summary="Initialize default stages")
async def initialize_default_stages(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Initialize default stages for the system.
    
    **Required Role:** Admin
    
    Creates the following default stages:
    - Stage 1: College Registration
    - Stage 2: Student Registration  
    - Stage 3: Application Processing
    - Stage 4: Results and Allotment
    - Completed: System Completed
    """
    try:
        stage_service = StageService(session)
        stage_ids = stage_service.initialize_default_stages()
        return {
            "message": "Default stages initialized successfully",
            "stage_ids": stage_ids,
            "stages_created": len(stage_ids)
        }
    except Exception as e:
        logger.error(f"Stage initialization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing stages: {str(e)}"
        )

@router.get("/check-registration/{role}", summary="Check if registration is allowed for role")
async def check_registration_allowed(
    role: str,
    session: Session = Depends(get_session)
):
    """
    Check if registration is currently allowed for a specific role.
    
    **Public endpoint** - No authentication required.
    
    **Parameters:**
    - role: The role to check (college, student, admin)
    
    **Returns:**
    - allowed: Boolean indicating if registration is allowed
    - current_stage: Information about the current stage
    - message: Human-readable message about the current state
    """
    try:
        from app.models.user import UserRole
        
        # Map string role to UserRole enum
        role_mapping = {
            "college": UserRole.COLLEGE,
            "student": UserRole.STUDENT,
            "admin": UserRole.ADMIN
        }
        
        if role.lower() not in role_mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}. Valid roles are: college, student, admin"
            )
        
        user_role = role_mapping[role.lower()]
        stage_service = StageService(session)
        
        is_allowed = stage_service.is_registration_allowed(user_role)
        current_stage_info = stage_service.get_stage_info()
        
        return {
            "allowed": is_allowed,
            "current_stage": current_stage_info.current_stage,
            "message": current_stage_info.stage_info.get("message", "No active stage"),
            "description": current_stage_info.stage_info.get("description", ""),
            "allowed_actions": current_stage_info.allowed_actions,
            "blocked_actions": current_stage_info.blocked_actions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking registration status: {str(e)}"
        )
