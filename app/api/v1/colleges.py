from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, File, UploadFile
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_session
from app.services.college_service import CollegeService
from app.services.file_service import FileService
from app.schemas.college import (
    CollegeSubmissionSchema, CollegeResponse, CollegeListResponse,
    CollegeVerificationResponse, CollegeBasicInfo, AddressSchema, ContactSchema,
    PrincipalSchema, SeatMatrixSchema, FacilitiesSchema, DocumentSchema, BankDetailsSchema
)
from app.middleware.auth import (
    get_current_user, require_admin, require_college
)
from app.models.user import CollegeProfile, User
from app.models.college import (
    CollegeVerificationStatus, VerificationStatus, CollegeType, CounsellingType,
    College, CollegePrincipal, CollegeSeatMatrix, CollegeFacilities, 
    CollegeDocuments, CollegeBankDetails
)
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
    type: str = Form("Private", description="College type (Private, Government, Aided, Self Financing)"),
    university_affiliation: Optional[str] = Form(None, description="University affiliation"),
    year_established: Optional[int] = Form(None, description="Year established"),
    naac_grade: Optional[str] = Form(None, description="NAAC grade"),
    nba_status: bool = Form(False, description="NBA status"),
    aicte_approved: bool = Form(False, description="AICTE approval status"),
    counselling_type: str = Form("UG", description="Counselling type (UG, PG, Diploma)"),
    
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
    
    # Documents (multiple files)
    document_files: List[UploadFile] = File(..., description="Document files"),
    
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
        # Validate enum values
        try:
            college_type = CollegeType(type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid college type: {type}. Valid values are: {[t.value for t in CollegeType]}"
            )
        
        try:
            counselling_type_enum = CounsellingType(counselling_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid counselling type: {counselling_type}. Valid values are: {[c.value for c in CounsellingType]}"
            )
        
        # Parse JSON strings
        try:
            seat_matrix_data = json.loads(seat_matrix)
            if not isinstance(seat_matrix_data, list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="seat_matrix must be a JSON array"
                )
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid seat_matrix JSON format: {str(e)}"
            )
        

        
        # Validate seat matrix data
        for i, seat_data in enumerate(seat_matrix_data):
            required_fields = ['course_name', 'intake_capacity', 'general_seats', 'sc_seats', 'st_seats', 'obc_seats', 'minority_seats']
            missing_fields = [field for field in required_fields if field not in seat_data]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Seat matrix item {i} missing required fields: {missing_fields}"
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
            type=college_type,
            university_affiliation=university_affiliation,
            year_established=year_established,
            naac_grade=naac_grade,
            nba_status=nba_status,
            aicte_approved=aicte_approved,
            counselling_type=counselling_type_enum,
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
            try:
                seat_matrix_schemas.append(SeatMatrixSchema(**seat_data))
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid seat matrix data: {str(e)}"
                )
        
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
        for doc_file in document_files:
            documents.append(DocumentSchema(
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
            detail=f"Internal server error: {str(e)}"
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
        
        # Generate signed URL for logo if it exists
        logo_url = None
        if college.logo_path:
            file_service = FileService()
            logo_url = file_service.get_signed_url(college.logo_path, 3600)
        
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
                "logo_url": logo_url,
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

@router.get("/all", summary="Get all colleges (Admin only)")
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
        from sqlmodel import select
        from app.models.user import UserRole
        
        # Query users with COLLEGE role and join with their profiles
        statement = (
            select(User, CollegeProfile)
            .join(CollegeProfile, User.id == CollegeProfile.user_id, isouter=True)  # Use left join to include users without profiles
            .where(User.role == UserRole.COLLEGE)
            .offset(skip)
            .limit(limit)
        )
        print('user.role', User.role)
        results = session.exec(statement).all()
        print(f'Debug: Found {len(results)} results')
        
        # Get total count for pagination
        count_statement = (
            select(User)
            .where(User.role == UserRole.COLLEGE)
        )
        total_count = len(session.exec(count_statement).all())
        print(f'Debug: Total users with COLLEGE role: {total_count}')
        print(f'Debug: Results: {results}')
        
        college_data = []
        for user, college_profile in results:
            print(f'Debug: Processing user {user.id}, college_profile: {college_profile}')
            
            # Get verification status for all colleges (not just approved ones)
            verification_status = None
            college = None
            
            # First get the main college record to get the correct college_id
            college_statement = select(College).where(College.user_id == user.id)
            college = session.exec(college_statement).first()
            
            # Now get verification status using the correct college_id
            if college:
                verification_statement = select(CollegeVerificationStatus).where(
                    CollegeVerificationStatus.college_id == college.id
                )
                verification_status = session.exec(verification_statement).first()
            
            # Include all COLLEGE users, with or without profiles
            college_info = {
                "user_id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "last_login": user.last_login,
                "college_profile": college_profile,
                "verification_status": verification_status.status if verification_status else "pending",
                "is_submitted": college_profile is not None,  # Add is_submitted key
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
            
            # If user has no college profile, set status to indicate they haven't submitted data
            if not college_profile:
                college_info["verification_status"] = "not_submitted"
                print(f'Debug: User {user.id} has no college profile - status: not_submitted')
            
            college_data.append(college_info)
        
        return {"data": college_data, "total_records": total_count}
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
        from sqlmodel import select
        from app.models.user import UserRole
        
        # Query user by college_id (which should be user_id) and COLLEGE role
        user_statement = (
            select(User)
            .where(User.id == college_id, User.role == UserRole.COLLEGE)
        )
        user = session.exec(user_statement).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College user not found"
            )
        
        # Get college profile
        college_profile_statement = (
            select(CollegeProfile)
            .where(CollegeProfile.user_id == user.id)
        )
        college_profile = session.exec(college_profile_statement).first()
        
        if not college_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College profile not found"
            )
        
        # Get main college data
        college_statement = (
            select(College)
            .where(College.user_id == user.id)
        )
        college = session.exec(college_statement).first()
        
        # Get principal information
        principal_statement = (
            select(CollegePrincipal)
            .where(CollegePrincipal.college_id == college.id if college else None)
        )
        principal = session.exec(principal_statement).first()
        
        # Get seat matrix
        seat_matrix_statement = (
            select(CollegeSeatMatrix)
            .where(CollegeSeatMatrix.college_id == college.id if college else None)
        )
        seat_matrix = session.exec(seat_matrix_statement).all()
        
        # Get facilities
        facilities_statement = (
            select(CollegeFacilities)
            .where(CollegeFacilities.college_id == college.id if college else None)
        )
        facilities = session.exec(facilities_statement).first()
        
        # Get documents
        documents_statement = (
            select(CollegeDocuments)
            .where(CollegeDocuments.college_id == college.id if college else None)
        )
        documents = session.exec(documents_statement).all()
        
        # Get bank details
        bank_details_statement = (
            select(CollegeBankDetails)
            .where(CollegeBankDetails.college_id == college.id if college else None)
        )
        bank_details = session.exec(bank_details_statement).first()
        
        # Get verification status
        verification_statement = (
            select(CollegeVerificationStatus)
            .where(CollegeVerificationStatus.college_id == college.id if college else None)
        )
        verification_status = session.exec(verification_statement).first()
        
        # Initialize file service for generating signed URLs
        file_service = FileService()
        
        # Build response data
        college_data = {
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "last_login": user.last_login,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            },
            "college_profile": {
                "id": college_profile.id,
                "college_name": college_profile.college_name,
                "college_code": college_profile.college_code,
                "address": college_profile.address,
                "district": college_profile.district,
                "state": college_profile.state,
                "contact_person": college_profile.contact_person,
                "contact_phone": college_profile.contact_phone,
                "website": college_profile.website,
                "is_approved": college_profile.is_approved,
                "approved_by_user_id": college_profile.approved_by_user_id,
                "approved_at": college_profile.approved_at,
                "created_at": college_profile.created_at,
                "updated_at": college_profile.updated_at
            }
        }
        
        # Add main college data if exists
        if college:
            # Generate signed URL for logo
            logo_url = None
            if college.logo_path:
                logo_url = file_service.get_signed_url(college.logo_path, 3600)
            
            college_data["college"] = {
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
                "logo_url": logo_url,
                "created_at": college.created_at,
                "updated_at": college.updated_at
            }
            
            # Add principal information
            if principal:
                # Generate signed URL for ID proof
                id_proof_url = None
                if principal.id_proof_path:
                    id_proof_url = file_service.get_signed_url(principal.id_proof_path, 3600)
                
                college_data["principal"] = {
                    "id": principal.id,
                    "name": principal.name,
                    "designation": principal.designation,
                    "phone": principal.phone,
                    "email": principal.email,
                    "id_proof_url": id_proof_url,
                    "created_at": principal.created_at,
                    "updated_at": principal.updated_at
                }
            
            # Add seat matrix
            if seat_matrix:
                college_data["seat_matrix"] = [
                    {
                        "id": seat.id,
                        "course_name": seat.course_name,
                        "intake_capacity": seat.intake_capacity,
                        "general_seats": seat.general_seats,
                        "sc_seats": seat.sc_seats,
                        "st_seats": seat.st_seats,
                        "obc_seats": seat.obc_seats,
                        "minority_seats": seat.minority_seats,
                        "created_at": seat.created_at,
                        "updated_at": seat.updated_at
                    }
                    for seat in seat_matrix
                ]
            
            # Add facilities
            if facilities:
                college_data["facilities"] = {
                    "id": facilities.id,
                    "hostel_available": facilities.hostel_available,
                    "transport_available": facilities.transport_available,
                    "wifi_available": facilities.wifi_available,
                    "lab_facilities": facilities.lab_facilities,
                    "placement_cell": facilities.placement_cell,
                    "created_at": facilities.created_at,
                    "updated_at": facilities.updated_at
                }
            
            # Add documents with signed URLs
            if documents:
                college_data["documents"] = []
                for doc in documents:
                    # Generate signed URL for document
                    doc_url = None
                    if doc.doc_path:
                        doc_url = file_service.get_signed_url(doc.doc_path, 3600)
                    
                    college_data["documents"].append({
                        "id": doc.id,
                        "doc_url": doc_url,
                        "file_name": doc.file_name,
                        "created_at": doc.created_at,
                        "updated_at": doc.updated_at
                    })
            
            # Add bank details
            if bank_details:
                # Generate signed URL for cancelled cheque
                cancelled_cheque_url = None
                if bank_details.cancelled_cheque_path:
                    cancelled_cheque_url = file_service.get_signed_url(bank_details.cancelled_cheque_path, 3600)
                
                college_data["bank_details"] = {
                    "id": bank_details.id,
                    "bank_name": bank_details.bank_name,
                    "branch": bank_details.branch,
                    "account_number": bank_details.account_number,
                    "ifsc_code": bank_details.ifsc_code,
                    "upi_id": bank_details.upi_id,
                    "cancelled_cheque_url": cancelled_cheque_url,
                    "created_at": bank_details.created_at,
                    "updated_at": bank_details.updated_at
                }
            
            # Add verification status
            if verification_status:
                college_data["verification_status"] = {
                    "id": verification_status.id,
                    "is_verified": verification_status.is_verified,
                    "verified_by": verification_status.verified_by,
                    "verification_notes": verification_status.verification_notes,
                    "rejected_reason": verification_status.rejected_reason,
                    "status": verification_status.status,
                    "created_at": verification_status.created_at,
                    "updated_at": verification_status.updated_at
                }
        
        return {
            "message": "College details retrieved successfully",
            "data": college_data
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