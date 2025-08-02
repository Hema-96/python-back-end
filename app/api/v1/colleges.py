from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, File, UploadFile
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_session
from app.services.college_service import CollegeService
from app.schemas.college import (
    CollegeSubmissionSchema, CollegeResponse, CollegeListResponse,
    CollegeVerificationResponse, CollegeBasicInfo, AddressSchema, ContactSchema,
    PrincipalSchema, SeatMatrixSchema, FacilitiesSchema, DocumentSchema, BankDetailsSchema
)
from app.middleware.auth import (
    get_current_user, require_admin, require_college
)
from app.models.user import User
from app.models.college import VerificationStatus, CollegeType, CounsellingType
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/colleges", tags=["Colleges"])

@router.post("/submit", summary="Submit college data for verification")
async def submit_college_data(
    # College basic info
    college_code: str = Form(..., description="Unique college code"),
    name: str = Form(..., description="College name"),
    short_name: Optional[str] = Form(None, description="Short name"),
    type: CollegeType = Form(CollegeType.PRIVATE, description="College type"),
    university_affiliation: Optional[str] = Form(None, description="University affiliation"),
    year_established: Optional[int] = Form(None, description="Year established"),
    naac_grade: Optional[str] = Form(None, description="NAAC grade"),
    nba_status: bool = Form(False, description="NBA status"),
    aicte_approved: bool = Form(False, description="AICTE approval status"),
    counselling_type: CounsellingType = Form(CounsellingType.UG, description="Counselling type"),
    
    # Address
    address_line1: str = Form(..., description="Address line 1"),
    address_line2: Optional[str] = Form(None, description="Address line 2"),
    city: str = Form(..., description="City"),
    district: str = Form(..., description="District"),
    state: str = Form("Tamil Nadu", description="State"),
    pincode: str = Form(..., description="Pincode"),
    
    # Contact
    phone: Optional[str] = Form(None, description="Phone number"),
    mobile: str = Form(..., description="Mobile number"),
    email: str = Form(..., description="Email address"),
    website: Optional[str] = Form(None, description="Website URL"),
    
    # Principal info
    principal_name: str = Form(..., description="Principal name"),
    principal_designation: Optional[str] = Form(None, description="Principal designation"),
    principal_phone: Optional[str] = Form(None, description="Principal phone"),
    principal_email: str = Form(..., description="Principal email"),
    
    # Seat matrix (JSON string)
    seat_matrix: str = Form(..., description="Seat matrix as JSON string"),
    
    # Facilities
    hostel_available: bool = Form(False, description="Hostel availability"),
    transport_available: bool = Form(False, description="Transport availability"),
    wifi_available: bool = Form(False, description="WiFi availability"),
    lab_facilities: Optional[str] = Form(None, description="Laboratory facilities"),
    placement_cell: bool = Form(False, description="Placement cell availability"),
    
    # Bank details
    bank_name: str = Form(..., description="Bank name"),
    branch: Optional[str] = Form(None, description="Branch name"),
    account_number: str = Form(..., description="Account number"),
    ifsc_code: str = Form(..., description="IFSC code"),
    upi_id: Optional[str] = Form(None, description="UPI ID"),
    
    # Files
    logo_file: Optional[UploadFile] = File(None, description="College logo file"),
    principal_id_proof_file: Optional[UploadFile] = File(None, description="Principal ID proof file"),
    cancelled_cheque_file: Optional[UploadFile] = File(None, description="Cancelled cheque file"),
    
    # Documents (multiple files with types)
    document_files: List[UploadFile] = File(..., description="Document files"),
    document_types: str = Form(..., description="Document types as JSON string"),
    
    current_user: User = Depends(require_college),
    session: Session = Depends(get_session)
):
    """
    Submit complete college data for admin verification.
    
    This endpoint allows college administrators to submit comprehensive college information
    including basic details, principal information, seat matrix, facilities, documents,
    and bank details. The submission will be pending admin approval.
    
    **Required Role:** College Administrator (Role 2)
    
    **Note:** This endpoint accepts multipart/form-data with files and form fields.
    """
    try:
        # Parse JSON strings
        try:
            seat_matrix_data = json.loads(seat_matrix)
            document_types_data = json.loads(document_types)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON format: {str(e)}"
            )
        
        # Validate document files and types match
        if len(document_files) != len(document_types_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Number of document files must match number of document types"
            )
        
        # Create address schema
        address = AddressSchema(
            line1=address_line1,
            line2=address_line2,
            city=city,
            district=district,
            state=state,
            pincode=pincode
        )
        
        # Create contact schema
        contact = ContactSchema(
            phone=phone,
            mobile=mobile,
            email=email,
            website=website
        )
        
        # Create college basic info
        college_info = CollegeBasicInfo(
            college_code=college_code,
            name=name,
            short_name=short_name,
            type=type,
            university_affiliation=university_affiliation,
            year_established=year_established,
            naac_grade=naac_grade,
            nba_status=nba_status,
            aicte_approved=aicte_approved,
            counselling_type=counselling_type,
            address=address,
            contact=contact,
            logo_file=logo_file
        )
        
        # Create principal schema
        principal = PrincipalSchema(
            name=principal_name,
            designation=principal_designation,
            phone=principal_phone,
            email=principal_email,
            id_proof_file=principal_id_proof_file
        )
        
        # Create seat matrix schemas
        seat_matrix_schemas = []
        for seat_data in seat_matrix_data:
            seat_matrix_schemas.append(SeatMatrixSchema(**seat_data))
        
        # Create facilities schema
        facilities = FacilitiesSchema(
            hostel_available=hostel_available,
            transport_available=transport_available,
            wifi_available=wifi_available,
            lab_facilities=lab_facilities,
            placement_cell=placement_cell
        )
        
        # Create document schemas
        documents = []
        for i, doc_file in enumerate(document_files):
            documents.append(DocumentSchema(
                doc_type=document_types_data[i],
                doc_file=doc_file
            ))
        
        # Create bank details schema
        bank_details = BankDetailsSchema(
            bank_name=bank_name,
            branch=branch,
            account_number=account_number,
            ifsc_code=ifsc_code,
            upi_id=upi_id,
            cancelled_cheque_file=cancelled_cheque_file
        )
        
        # Create complete submission schema
        college_data = CollegeSubmissionSchema(
            college=college_info,
            principal=principal,
            seat_matrix=seat_matrix_schemas,
            facilities=facilities,
            documents=documents,
            bank_details=bank_details
        )
        
        college_service = CollegeService(session)
        result = college_service.submit_college_data(current_user.id, college_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"College data submission error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

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
        colleges = college_service.get_colleges_by_user(current_user.id)
        
        if not colleges:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No college data found for this user"
            )
        
        # Return the first college (assuming one college per user)
        college = colleges[0]
        
        return {
            "message": "College data retrieved successfully",
            "data": {
                "id": college.id,
                "college_code": college.college_code,
                "name": college.name,
                "short_name": college.short_name,
                "type": college.type,
                "city": college.city,
                "district": college.district,
                "state": college.state,
                "logo_url": college.logo_url,
                "created_at": college.created_at,
                "updated_at": college.updated_at
            }
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
    limit: int = Query(20, ge=1, le=100, description="Number of records to return")
):
    """
    Get all colleges with pagination.
    
    **Required Role:** Admin (Role 1)
    """
    try:
        college_service = CollegeService(session)
        colleges = college_service.get_all_colleges(skip=skip, limit=limit)
        
        result = []
        for college in colleges:
            # Get verification status for each college
            from sqlmodel import select
            statement = select(CollegeVerificationStatus).where(CollegeVerificationStatus.college_id == college.id)
            verification_status = session.exec(statement).first()
            
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
        college = college_service.get_college_by_id(college_id)
        
        if not college:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College not found"
            )
        
        return {
            "message": "College details retrieved successfully",
            "data": {
                "id": college.id,
                "college_code": college.college_code,
                "name": college.name,
                "short_name": college.short_name,
                "type": college.type,
                "university_affiliation": college.university_affiliation,
                "year_established": college.year_established,
                "naac_grade": college.naac_grade,
                "nba_status": college.nba_status,
                "aicte_approved": college.aicte_approved,
                "counselling_type": college.counselling_type,
                "address_line1": college.address_line1,
                "address_line2": college.address_line2,
                "city": college.city,
                "district": college.district,
                "state": college.state,
                "pincode": college.pincode,
                "phone": college.phone,
                "mobile": college.mobile,
                "email": college.email,
                "website": college.website,
                "logo_url": college.logo_url,
                "created_at": college.created_at,
                "updated_at": college.updated_at
            }
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
        result = college_service.update_college_verification(
            college_id=college_id,
            is_verified=is_approved,
            verified_by=current_user.id,
            notes=notes
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
        colleges = college_service.get_all_colleges(skip=skip, limit=limit)
        
        result = []
        for college in colleges:
            # Get verification status for each college
            from sqlmodel import select
            statement = select(CollegeVerificationStatus).where(
                CollegeVerificationStatus.college_id == college.id,
                CollegeVerificationStatus.status == VerificationStatus.PENDING
            )
            verification_status = session.exec(statement).first()
            
            if verification_status:
                result.append(CollegeListResponse(
                    id=college.id,
                    college_code=college.college_code,
                    name=college.name,
                    type=college.type,
                    city=college.city,
                    district=college.district,
                    status=verification_status.status,
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
        colleges = college_service.get_all_colleges(skip=skip, limit=limit)
        
        result = []
        for college in colleges:
            # Get verification status for each college
            from sqlmodel import select
            statement = select(CollegeVerificationStatus).where(
                CollegeVerificationStatus.college_id == college.id,
                CollegeVerificationStatus.status == VerificationStatus.APPROVED
            )
            verification_status = session.exec(statement).first()
            
            if verification_status:
                result.append(CollegeListResponse(
                    id=college.id,
                    college_code=college.college_code,
                    name=college.name,
                    type=college.type,
                    city=college.city,
                    district=college.district,
                    status=verification_status.status,
                    created_at=college.created_at
                ))
        
        return result
    except Exception as e:
        logger.error(f"Error getting approved colleges: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 