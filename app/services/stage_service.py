from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.access_control import Stage, StageType, StagePermission, Permission
from app.schemas.access_control import (
    StageCreate, StageUpdate, StageResponse, 
    StagePermissionCreate, CurrentStageResponse
)
from app.models.user import UserRole
import logging

logger = logging.getLogger(__name__)

class StageService:
    def __init__(self, session: Session):
        self.session = session

    def create_stage(self, stage_data: StageCreate, created_by: int) -> StageResponse:
        """Create a new stage"""
        try:
            # Deactivate all other stages if this one is active
            if stage_data.is_active:
                self._deactivate_all_stages()
            
            stage = Stage(
                **stage_data.dict(),
                created_by=created_by
            )
            self.session.add(stage)
            self.session.commit()
            self.session.refresh(stage)
            
            logger.info(f"Stage '{stage.name}' created by user {created_by}")
            return StageResponse.from_orm(stage)
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating stage: {e}")
            raise

    def update_stage(self, stage_id: int, stage_data: StageUpdate) -> StageResponse:
        """Update an existing stage"""
        try:
            stage = self.session.get(Stage, stage_id)
            if not stage:
                raise ValueError(f"Stage with id {stage_id} not found")
            
            # Deactivate all other stages if this one is being activated
            if stage_data.is_active and not stage.is_active:
                self._deactivate_all_stages()
            
            update_data = stage_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(stage, field, value)
            
            stage.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(stage)
            
            logger.info(f"Stage '{stage.name}' updated")
            return StageResponse.from_orm(stage)
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating stage: {e}")
            raise

    def get_current_stage(self) -> Optional[StageResponse]:
        """Get the currently active stage"""
        try:
            statement = select(Stage).where(Stage.is_active == True)
            stage = self.session.exec(statement).first()
            return StageResponse.from_orm(stage) if stage else None
        except Exception as e:
            logger.error(f"Error getting current stage: {e}")
            raise

    def get_stage_by_type(self, stage_type: StageType) -> Optional[StageResponse]:
        """Get stage by type"""
        try:
            statement = select(Stage).where(Stage.stage_type == stage_type)
            stage = self.session.exec(statement).first()
            return StageResponse.from_orm(stage) if stage else None
        except Exception as e:
            logger.error(f"Error getting stage by type: {e}")
            raise

    def activate_stage(self, stage_id: int) -> StageResponse:
        """Activate a specific stage and deactivate others"""
        try:
            # Deactivate all stages
            self._deactivate_all_stages()
            
            # Activate the specified stage
            stage = self.session.get(Stage, stage_id)
            if not stage:
                raise ValueError(f"Stage with id {stage_id} not found")
            
            stage.is_active = True
            stage.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(stage)
            
            logger.info(f"Stage '{stage.name}' activated")
            return StageResponse.from_orm(stage)
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error activating stage: {e}")
            raise

    def deactivate_stage(self, stage_id: int) -> StageResponse:
        """Deactivate a specific stage"""
        try:
            stage = self.session.get(Stage, stage_id)
            if not stage:
                raise ValueError(f"Stage with id {stage_id} not found")
            
            stage.is_active = False
            stage.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(stage)
            
            logger.info(f"Stage '{stage.name}' deactivated")
            return StageResponse.from_orm(stage)
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deactivating stage: {e}")
            raise

    def get_all_stages(self) -> List[StageResponse]:
        """Get all stages"""
        try:
            statement = select(Stage).order_by(Stage.created_at)
            stages = self.session.exec(statement).all()
            return [StageResponse.from_orm(stage) for stage in stages]
        except Exception as e:
            logger.error(f"Error getting all stages: {e}")
            raise

    def is_registration_allowed(self, user_role: UserRole) -> bool:
        """Check if registration is allowed for the given user role in current stage"""
        try:
            current_stage = self.get_current_stage()
            if not current_stage:
                return False
            
            # Stage 1: Only college registration allowed
            if current_stage.stage_type == StageType.STAGE_1:
                return user_role == UserRole.COLLEGE
            
            # Stage 2: Only student registration allowed
            elif current_stage.stage_type == StageType.STAGE_2:
                return user_role == UserRole.STUDENT
            
            # Other stages: No registration allowed
            else:
                return False
        except Exception as e:
            logger.error(f"Error checking registration permission: {e}")
            return False

    def is_endpoint_allowed(self, endpoint_path: str, user_roles: List[str]) -> bool:
        """Check if an endpoint is allowed in the current stage"""
        try:
            current_stage = self.get_current_stage()
            if not current_stage:
                return True  # If no stage is active, allow all endpoints
            
            # Check if endpoint is explicitly blocked
            if endpoint_path in current_stage.blocked_endpoints:
                return False
            
            # Check if user has required role for current stage
            if current_stage.allowed_roles and not any(role in current_stage.allowed_roles for role in user_roles):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking endpoint permission: {e}")
            return False

    def get_stage_info(self) -> CurrentStageResponse:
        """Get comprehensive information about the current stage"""
        try:
            current_stage = self.get_current_stage()
            if not current_stage:
                return CurrentStageResponse(
                    current_stage=None,
                    allowed_actions=[],
                    blocked_actions=[],
                    stage_info={"message": "No active stage"}
                )
            
            # Determine allowed and blocked actions based on stage
            allowed_actions = []
            blocked_actions = []
            
            if current_stage.stage_type == StageType.STAGE_1:
                allowed_actions = ["college_registration", "college_login", "college_profile_update"]
                blocked_actions = ["student_registration", "student_login"]
                stage_info = {
                    "message": "College Registration Phase",
                    "description": "Colleges can register and submit their details",
                    "next_stage": "Student Registration"
                }
            elif current_stage.stage_type == StageType.STAGE_2:
                allowed_actions = ["student_registration", "student_login", "student_profile_update"]
                blocked_actions = ["college_registration", "college_login"]
                stage_info = {
                    "message": "Student Registration Phase",
                    "description": "Students can register and submit their details",
                    "next_stage": "Application Processing"
                }
            elif current_stage.stage_type == StageType.STAGE_3:
                allowed_actions = ["application_processing", "admin_review"]
                blocked_actions = ["college_registration", "student_registration"]
                stage_info = {
                    "message": "Application Processing Phase",
                    "description": "Applications are being processed and reviewed",
                    "next_stage": "Results and Allotment"
                }
            elif current_stage.stage_type == StageType.STAGE_4:
                allowed_actions = ["results_view", "allotment_view"]
                blocked_actions = ["college_registration", "student_registration", "application_processing"]
                stage_info = {
                    "message": "Results and Allotment Phase",
                    "description": "Results are published and allotments are made",
                    "next_stage": "Completed"
                }
            else:
                allowed_actions = ["view_only"]
                blocked_actions = ["all_registration", "all_processing"]
                stage_info = {
                    "message": "System Completed",
                    "description": "All stages completed",
                    "next_stage": "None"
                }
            
            return CurrentStageResponse(
                current_stage=current_stage,
                allowed_actions=allowed_actions,
                blocked_actions=blocked_actions,
                stage_info=stage_info
            )
        except Exception as e:
            logger.error(f"Error getting stage info: {e}")
            raise

    def _deactivate_all_stages(self):
        """Deactivate all stages"""
        try:
            stages = self.session.exec(select(Stage)).all()
            for stage in stages:
                stage.is_active = False
                stage.updated_at = datetime.utcnow()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deactivating all stages: {e}")
            raise

    def initialize_default_stages(self) -> Dict[str, int]:
        """Initialize default stages if they don't exist"""
        try:
            created_count = 0
            stage_ids = {}
            
            default_stages = [
                {
                    "stage_type": StageType.STAGE_1,
                    "name": "College Registration",
                    "description": "Stage 1: Colleges can register and submit their details",
                    "allowed_roles": ["college"],
                    "blocked_endpoints": ["/api/auth/register/student", "/api/students/submit"],
                    "required_permissions": ["college:register", "college:submit"]
                },
                {
                    "stage_type": StageType.STAGE_2,
                    "name": "Student Registration",
                    "description": "Stage 2: Students can register and submit their details",
                    "allowed_roles": ["student"],
                    "blocked_endpoints": ["/api/auth/register/college", "/api/colleges/submit"],
                    "required_permissions": ["student:register", "student:submit"]
                },
                {
                    "stage_type": StageType.STAGE_3,
                    "name": "Application Processing",
                    "description": "Stage 3: Applications are being processed and reviewed",
                    "allowed_roles": ["admin"],
                    "blocked_endpoints": ["/api/auth/register"],
                    "required_permissions": ["admin:process", "admin:review"]
                },
                {
                    "stage_type": StageType.STAGE_4,
                    "name": "Results and Allotment",
                    "description": "Stage 4: Results are published and allotments are made",
                    "allowed_roles": ["admin", "college", "student"],
                    "blocked_endpoints": ["/api/auth/register", "/api/colleges/submit", "/api/students/submit"],
                    "required_permissions": ["results:view", "allotment:view"]
                },
                {
                    "stage_type": StageType.COMPLETED,
                    "name": "System Completed",
                    "description": "All stages completed",
                    "allowed_roles": ["admin"],
                    "blocked_endpoints": ["/api/auth/register", "/api/colleges/submit", "/api/students/submit"],
                    "required_permissions": ["admin:view"]
                }
            ]
            
            for stage_data in default_stages:
                existing_stage = self.get_stage_by_type(stage_data["stage_type"])
                if not existing_stage:
                    stage_create = StageCreate(**stage_data)
                    stage = self.create_stage(stage_create, created_by=1)  # Admin user ID 1
                    stage_ids[stage_data["stage_type"]] = stage.id
                    created_count += 1
            
            if created_count > 0:
                logger.info(f"Created {created_count} default stages")
            
            return stage_ids
        except Exception as e:
            logger.error(f"Error initializing default stages: {e}")
            raise
