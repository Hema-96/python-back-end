from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_session
from app.services.college_service import CollegeService
from app.schemas.college import (
    CollegeSubmissionSchema, CollegeResponse, CollegeListResponse,
    CollegeVerificationResponse
)
from app.middleware.auth import (
    get_current_user, require_admin, require_college
)
from app.models.user import User
from app.models.college import VerificationStatus
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/colleges", tags=["Colleges"])

@router.post("/submit", summary="Submit college data for verification")
async def submit_college_data(
    college_data: CollegeSubmissionSchema,
    current_user: User = Depends(require_college),
    session: Session = Depends(get_session)
):
    """
    Submit complete college data for admin verification.
    
    This endpoint allows college administrators to submit comprehensive college information
    including basic details, principal information, seat matrix, facilities, documents,
    and bank details. The submission will be pending admin approval.
    
    **Required Role:** College Administrator (Role 2)
    """
    try:
        college_service = CollegeService(session)
        result = college_service.submit_college_data(current_user.id, college_data)
        return result
    except Exception as e:
        logger.error(f"College data submission error: {e}")
        raise

@router.get("/my-college", summary="Get current user's college data")
async def get_my_college(
    current_user: User = Depends(require_college),
    session: Session = Depends(get_session)
):
    """
    Get the college data for the current college administrator.
    
    **Required Role:** College Administrator (Role 2)
    """
    try:
        college_service = CollegeService(session)
        college = college_service.get_college_by_user(current_user.id)
        
        if not college:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No college data found for this user"
            )
        
        # Get complete college details
        college_details = college_service.get_college_details(college.id)
        if not college_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College details not found"
            )
        
        return {
            "message": "College data retrieved successfully",
            "data": college_details
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting college data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/all", response_model=List[CollegeListResponse], summary="Get all colleges (Admin only)")
async def get_all_colleges(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    status: Optional[VerificationStatus] = Query(None, description="Filter by verification status")
):
    """
    Get all colleges with optional filtering by verification status.
    
    **Required Role:** Admin (Role 1)
    """
    try:
        college_service = CollegeService(session)
        colleges = college_service.get_all_colleges(skip=skip, limit=limit, status=status)
        
        result = []
        for college_data in colleges:
            college = college_data["college"]
            verification_status = college_data["verification_status"]
            
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
        
        return result
    except Exception as e:
        logger.error(f"Error getting all colleges: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{college_id}", summary="Get detailed college information (Admin only)")
async def get_college_details(
    college_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get detailed information about a specific college.
    
    **Required Role:** Admin (Role 1)
    """
    try:
        college_service = CollegeService(session)
        college_details = college_service.get_college_details(college_id)
        
        if not college_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College not found"
            )
        
        return {
            "message": "College details retrieved successfully",
            "data": college_details
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting college details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/{college_id}/verify", summary="Verify or reject college (Admin only)")
async def verify_college(
    college_id: int,
    is_approved: bool = Query(..., description="Whether to approve or reject the college"),
    notes: Optional[str] = Query(None, description="Verification notes"),
    rejected_reason: Optional[str] = Query(None, description="Reason for rejection (if rejected)"),
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Verify or reject a college submission.
    
    **Required Role:** Admin (Role 1)
    
    - **is_approved**: True to approve, False to reject
    - **notes**: Optional verification notes
    - **rejected_reason**: Required if rejecting the college
    """
    try:
        if not is_approved and not rejected_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rejection reason is required when rejecting a college"
            )
        
        college_service = CollegeService(session)
        result = college_service.verify_college(
            college_id=college_id,
            admin_user_id=current_user.id,
            is_approved=is_approved,
            notes=notes,
            rejected_reason=rejected_reason
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying college: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/pending", response_model=List[CollegeListResponse], summary="Get pending colleges (Admin only)")
async def get_pending_colleges(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return")
):
    """
    Get all colleges pending verification.
    
    **Required Role:** Admin (Role 1)
    """
    try:
        college_service = CollegeService(session)
        colleges = college_service.get_all_colleges(
            skip=skip, 
            limit=limit, 
            status=VerificationStatus.PENDING
        )
        
        result = []
        for college_data in colleges:
            college = college_data["college"]
            verification_status = college_data["verification_status"]
            
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
        
        return result
    except Exception as e:
        logger.error(f"Error getting pending colleges: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/approved", response_model=List[CollegeListResponse], summary="Get approved colleges")
async def get_approved_colleges(
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return")
):
    """
    Get all approved colleges (public endpoint).
    """
    try:
        college_service = CollegeService(session)
        colleges = college_service.get_all_colleges(
            skip=skip, 
            limit=limit, 
            status=VerificationStatus.APPROVED
        )
        
        result = []
        for college_data in colleges:
            college = college_data["college"]
            verification_status = college_data["verification_status"]
            
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
        
        return result
    except Exception as e:
        logger.error(f"Error getting approved colleges: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 