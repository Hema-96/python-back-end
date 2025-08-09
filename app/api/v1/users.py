from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from app.core.database import get_session
from app.services.auth_service import AuthService
from app.schemas.user import (
    AdminProfileCreate, AdminProfileResponse,
    CollegeProfileCreate, CollegeProfileResponse,
    StudentProfileCreate, StudentProfileResponse, 
    UserUpdate, UserListResponse
)
from app.middleware.auth import (
    get_current_user, require_admin, require_college, 
    require_student, require_any_role
)
from app.models.user import User, AdminProfile, CollegeProfile, StudentProfile, UserRole
from app.models.college import College, CollegeVerificationStatus, VerificationStatus
from app.schemas.college import CollegeListResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])

# Profile Management Endpoints
@router.post("/admin/profile", response_model=AdminProfileResponse, summary="Create admin profile")
async def create_admin_profile(
    profile_data: AdminProfileCreate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Create admin profile for the current user.
    
    Requires admin role.
    """
    try:
        auth_service = AuthService(session)
        return auth_service.create_admin_profile(current_user.id, profile_data)
    except Exception as e:
        logger.error(f"Admin profile creation error: {e}")
        raise

@router.post("/college/profile", response_model=CollegeProfileResponse, summary="Create college profile")
async def create_college_profile(
    profile_data: CollegeProfileCreate,
    current_user: User = Depends(require_college),
    session: Session = Depends(get_session)
):
    """
    Create college profile for the current user.
    
    Requires college role.
    """
    try:
        auth_service = AuthService(session)
        return auth_service.create_college_profile(current_user.id, profile_data)
    except Exception as e:
        logger.error(f"College profile creation error: {e}")
        raise

@router.post("/student/profile", response_model=StudentProfileResponse, summary="Create student profile")
async def create_student_profile(
    profile_data: StudentProfileCreate,
    current_user: User = Depends(require_student),
    session: Session = Depends(get_session)
):
    """
    Create student profile for the current user.
    
    Requires student role.
    """
    try:
        auth_service = AuthService(session)
        return auth_service.create_student_profile(current_user.id, profile_data)
    except Exception as e:
        logger.error(f"Student profile creation error: {e}")
        raise

# Profile Retrieval Endpoints
@router.get("/admin/profile", response_model=AdminProfileResponse, summary="Get admin profile")
async def get_admin_profile(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get admin profile for the current user.
    
    Requires admin role.
    """
    statement = select(AdminProfile).where(AdminProfile.user_id == current_user.id)
    profile = session.exec(statement).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin profile not found"
        )
    return profile

@router.get("/college/profile", response_model=CollegeProfileResponse, summary="Get college profile")
async def get_college_profile(
    current_user: User = Depends(require_college),
    session: Session = Depends(get_session)
):
    """
    Get college profile for the current user.
    
    Requires college role.
    """
    statement = select(CollegeProfile).where(CollegeProfile.user_id == current_user.id)
    profile = session.exec(statement).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="College profile not found"
        )
    return profile

@router.get("/student/profile", response_model=StudentProfileResponse, summary="Get student profile")
async def get_student_profile(
    current_user: User = Depends(require_student),
    session: Session = Depends(get_session)
):
    """
    Get student profile for the current user.
    
    Requires student role.
    """
    statement = select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    profile = session.exec(statement).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    return profile

# Admin-only endpoints
@router.get("/all", summary="Get all users")
async def get_all_users(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    format: str = Query("standard", description="Response format: 'standard' or 'dashboard'")
):
    """
    Get all users with pagination and filtering (excluding admin users).
    
    **Formats:**
    - **standard**: Returns UserListResponse objects (default)
    - **dashboard**: Returns formatted data for admin dashboard with status, lastLogin formatting, etc.
    
    **Note:** Admin users (role_id = 1) are excluded from the results.
    
    Requires admin role.
    """
    try:
        statement = select(User)
        
        # Exclude admin users (role_id != 1) from the results
        statement = statement.where(User.role != UserRole.ADMIN)
        
        if role:
            statement = statement.where(User.role == role)
        if is_active is not None:
            statement = statement.where(User.is_active == is_active)
            
        statement = statement.offset(skip).limit(limit)
        users = session.exec(statement).all()
        
        if format == "dashboard":
            # Return dashboard format
            from app.services.admin_service import AdminService
            admin_service = AdminService(session)
            return {"data": admin_service.format_users_for_dashboard(users)}
        else:
            # Return standard format
            return [
                UserListResponse(
                    id=user.id,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    role=user.role,
                    is_active=user.is_active,
                    last_login=user.last_login,
                    is_verified=user.is_verified,
                    created_at=user.created_at
                )
                for user in users
            ]
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/colleges", summary="Get all colleges")
async def get_all_colleges(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    approved_only: bool = Query(False, description="Show only approved colleges")
):
    """
    Get all colleges with pagination.
    
    Requires admin role.
    """
    try:
        # Query colleges with their verification status
        statement = select(College).offset(skip).limit(limit)
        
        if approved_only:
            # Join with verification status to filter approved colleges
            statement = (
                select(College)
                .join(CollegeVerificationStatus, College.id == CollegeVerificationStatus.college_id)
                .where(CollegeVerificationStatus.status == VerificationStatus.APPROVED)
                .offset(skip)
                .limit(limit)
            )
        
        colleges = session.exec(statement).all()
        
        result = []
        for college in colleges:
            # Get verification status for each college
            verification_statement = select(CollegeVerificationStatus).where(
                CollegeVerificationStatus.college_id == college.id
            )
            verification_status = session.exec(verification_statement).first()
            
            result.append(CollegeListResponse(
                id=college.id,
                college_code=college.college_code,
                name=college.name,
                type=college.type,
                city=college.city,
                district=college.district,
                status=verification_status.status if verification_status else VerificationStatus.PENDING,
                created_at=college.created_at
            ))
        
        return {"data": result, "total_records": len(result)}
    except Exception as e:
        logger.error(f"Error fetching colleges: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/college/{college_id}/approve", summary="Approve a college")
async def approve_college(
    college_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Approve a college profile.
    
    Requires admin role.
    """
    try:
        statement = select(CollegeProfile).where(CollegeProfile.id == college_id)
        college = session.exec(statement).first()
        
        if not college:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College not found"
            )
        
        college.is_approved = True
        college.approved_by_user_id = current_user.id
        college.approved_at = datetime.utcnow()
        college.updated_at = datetime.utcnow()
        
        session.add(college)
        session.commit()
        session.refresh(college)
        
        logger.info(f"College {college_id} approved by admin {current_user.id}")
        return {"message": "College approved successfully", "college": college}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving college: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/profile", summary="Update user profile")
async def update_user_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update current user's profile information.
    
    Requires authentication.
    """
    try:
        if profile_data.first_name is not None:
            current_user.first_name = profile_data.first_name
        if profile_data.last_name is not None:
            current_user.last_name = profile_data.last_name
        if profile_data.phone is not None:
            current_user.phone = profile_data.phone
        
        current_user.updated_at = datetime.utcnow()
        
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        
        return {"message": "Profile updated successfully", "user": current_user}
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{user_id}", summary="Delete user")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Delete a user (admin only).
    
    Requires admin role.
    """
    try:
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        session.delete(user)
        session.commit()
        
        logger.info(f"User {user_id} deleted by admin {current_user.id}")
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 