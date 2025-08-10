from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, File, UploadFile
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from app.core.database import get_session
from app.services.student_service import StudentService
from app.services.file_service import FileService
from app.schemas.student import (
    StudentSubmissionSchema, StudentResponse, StudentListResponse,
    StudentVerificationResponse, StudentPersonalInfo, StudentAcademicInfo,
    StudentDocumentsResponse, StudentDocumentsListResponse
)
from app.middleware.auth import (
    get_current_user, require_admin, require_student
)
from app.models.user import User
from app.models.student import (
    Student, StudentDocuments, StudentVerificationStatus, VerificationStatus, Gender, CasteCategory
)
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/submit", summary="Submit student data for verification")
async def submit_student_data(
    # Personal info
    date_of_birth: str = Form(..., description="Date of birth (YYYY-MM-DD)"),
    gender: str = Form(..., description="Gender (Male, Female, Other)"),
    address_line1: str = Form(..., description="Address line 1"),
    address_line2: Optional[str] = Form(None, description="Address line 2"),
    city: str = Form(..., description="City"),
    district: str = Form(..., description="District"),
    state: str = Form("Tamil Nadu", description="State"),
    pincode: str = Form(..., description="Pincode"),
    
    # Academic info
    parent_name: str = Form(..., description="Parent/Guardian name"),
    parent_phone: str = Form(..., description="Parent/Guardian phone"),
    parent_email: Optional[str] = Form(None, description="Parent/Guardian email"),
    caste_category: str = Form(..., description="Caste category"),
    annual_income: Optional[float] = Form(None, description="Annual family income"),
    minority_status: bool = Form(False, description="Minority status"),
    physically_challenged: bool = Form(False, description="Physically challenged status"),
    sports_quota: bool = Form(False, description="Sports quota eligibility"),
    ncc_quota: bool = Form(False, description="NCC quota eligibility"),
    
    # Documents (multiple files)
    document_files: List[UploadFile] = File(..., description="Document files"),
    
    current_user: User = Depends(require_student),
    session: Session = Depends(get_session)
):
    """
    Submit complete student data for admin verification.
    
    This endpoint allows students to submit comprehensive information
    including personal details, academic information, and required documents.
    The submission will be pending admin approval.
    
    **Required Role:** Student (Role 3)
    
    **Note:** This endpoint accepts multipart/form-data with files and form fields.
    """
    try:
        # Validate enum values
        try:
            gender_enum = Gender(gender)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid gender: {gender}. Valid values are: {[g.value for g in Gender]}"
            )
        
        try:
            caste_category_enum = CasteCategory(caste_category)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid caste category: {caste_category}. Valid values are: {[c.value for c in CasteCategory]}"
            )
        
        # Parse date of birth
        try:
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
        

        
        # Create personal info schema
        personal_info = StudentPersonalInfo(
            date_of_birth=dob,
            gender=gender_enum,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            district=district,
            state=state,
            pincode=pincode
        )
        
        # Create academic info schema
        academic_info = StudentAcademicInfo(
            parent_name=parent_name,
            parent_phone=parent_phone,
            parent_email=parent_email,
            caste_category=caste_category_enum,
            annual_income=annual_income,
            minority_status=minority_status,
            physically_challenged=physically_challenged,
            sports_quota=sports_quota,
            ncc_quota=ncc_quota
        )
        
        # Create complete submission schema
        student_data = StudentSubmissionSchema(
            personal_info=personal_info,
            academic_info=academic_info,
            documents=[]  # Empty list, will be populated in service
        )
        
        student_service = StudentService(session)
        result = student_service.submit_student_data(current_user.id, student_data, document_files)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Student data submission error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/my-profile", summary="Get current user's student profile")
async def get_my_student_profile(
    current_user: User = Depends(require_student),
    session: Session = Depends(get_session)
):
    """
    Get the current student's profile information.
    
    **Required Role:** Student (Role 3)
    """
    try:
        student_service = StudentService(session)
        student = student_service.get_student_by_user_id(current_user.id)
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )
        
        # Get verification status
        verification = session.exec(
            select(StudentVerificationStatus).where(StudentVerificationStatus.user_id == current_user.id)
        ).first()
        
        numeric_status = 1  # Default to pending
        if verification:
            if verification.status == VerificationStatus.APPROVED:
                numeric_status = 2
            elif verification.status == VerificationStatus.REJECTED:
                numeric_status = 3
        
        return {
            "student": {
                "id": student.id,
                "user_id": student.user_id,
                "date_of_birth": student.date_of_birth,
                "gender": student.gender,
                "address_line1": student.address_line1,
                "address_line2": student.address_line2,
                "city": student.city,
                "district": student.district,
                "state": student.state,
                "pincode": student.pincode,
                "parent_name": student.parent_name,
                "parent_phone": student.parent_phone,
                "parent_email": student.parent_email,
                "caste_category": student.caste_category,
                "annual_income": student.annual_income,
                "minority_status": student.minority_status,
                "physically_challenged": student.physically_challenged,
                "sports_quota": student.sports_quota,
                "ncc_quota": student.ncc_quota,
                "created_at": student.created_at,
                "updated_at": student.updated_at
            },
            "verification_status": numeric_status,
            "verification_details": verification.dict() if verification else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/all", summary="Get all students (Admin only)")
async def get_all_students(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return")
):
    """
    Get all students with pagination.
    
    **Required Role:** Admin (Role 1)
    """
    try:
        from app.models.user import UserRole
        
        # Query users with STUDENT role and join with their student profiles
        statement = (
            select(User, Student)
            .join(Student, User.id == Student.user_id, isouter=True)  # Use left join to include users without profiles
            .where(User.role == UserRole.STUDENT)
            .offset(skip)
            .limit(limit)
        )
        
        results = session.exec(statement).all()
        
        # Get total count for pagination
        count_statement = (
            select(User)
            .where(User.role == UserRole.STUDENT)
        )
        total_count = len(session.exec(count_statement).all())
        
        student_data = []
        for user, student in results:
            # Get verification status for all students (not just approved ones)
            verification_status = None
            student_record = None
            
            # First get the main student record to get the correct student_id
            student_statement = select(Student).where(Student.user_id == user.id)
            student_record = session.exec(student_statement).first()
            
            # Now get verification status using the correct user_id
            if student_record:
                verification_statement = select(StudentVerificationStatus).where(
                    StudentVerificationStatus.user_id == user.id
                )
                verification_status = session.exec(verification_statement).first()
            
            # Determine numeric status based on verification status
            if not verification_status:
                status = 1  # Pending - no entry in verification table
            elif verification_status.status == "approved":
                status = 2  # Approved - entry exists with status APPROVED
            elif verification_status.status == "rejected":
                status = 3  # Rejected - entry exists with status REJECTED
            else:
                status = 1  # Default to pending for any other status
            
            # Include all STUDENT users, with or without profiles
            student_info = {
                "user_id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "last_login": user.last_login,
                "student_profile": student,
                "status": status,  # New numeric status field
                "verification_status": verification_status.status if verification_status else "pending",
                "is_submitted": student is not None,  # Add is_submitted key
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
            
            # If user has no student profile, set status to indicate they haven't submitted data
            if not student:
                student_info["verification_status"] = "not_submitted"
                student_info["status"] = 1  # Set numeric status to pending for users without profiles
            
            student_data.append(student_info)
        
        return {"data": student_data, "total_records": total_count}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all students: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/pending", response_model=List[StudentListResponse], summary="Get pending students (Admin only)")
async def get_pending_students(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return")
):
    """
    Get pending students with pagination.
    
    **Required Role:** Admin (Role 1)
    """
    try:
        student_service = StudentService(session)
        students = student_service.get_pending_students(skip, limit)
        return students
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pending students: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/approved", response_model=List[StudentListResponse], summary="Get approved students")
async def get_approved_students(
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return")
):
    """
    Get approved students with pagination.
    
    **Public endpoint** - No authentication required
    """
    try:
        student_service = StudentService(session)
        students = student_service.get_approved_students(skip, limit)
        return students
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting approved students: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/{user_id}/verify", summary="Verify or reject student (Admin only)")
async def verify_student(
    user_id: int,
    verification_data: dict,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Verify or reject a student's submission.
    
    **Required Role:** Admin (Role 1)
    
    **Request Body:**
    - status: "APPROVED" or "REJECTED"
    - remarks: Optional remarks from admin
    """
    try:
        status_value = verification_data.get("status")
        remarks = verification_data.get("remarks")
        
        if not status_value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status is required"
            )
        
        try:
            verification_status = VerificationStatus(status_value)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_value}. Valid values are: {[s.value for s in VerificationStatus]}"
            )
        
        student_service = StudentService(session)
        result = student_service.update_student_verification(
            user_id, 
            verification_status, 
            remarks, 
            current_user.id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying student: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{student_id}/documents", summary="Get student documents")
async def get_student_documents(
    student_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all documents for a specific student.
    
    **Required Role:** Student (Role 3) - can only access their own documents
    **Admin Role:** Admin (Role 1) - can access any student documents
    
    Returns a structured response with documents list and metadata.
    """
    try:
        from app.models.user import UserRole
        
        # Check if user is admin or owns the student profile
        if current_user.role != UserRole.ADMIN:  # Not admin
            # Get the student to check ownership
            statement = select(Student).where(Student.id == student_id)
            student = session.exec(statement).first()
            
            if not student:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Student not found"
                )
            
            if student.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. You can only access your own documents."
                )
        
        # Get all documents for the student
        statement = select(StudentDocuments).where(StudentDocuments.student_id == student_id)
        documents = session.exec(statement).all()
        
        if not documents:
            return StudentDocumentsListResponse(
                data=[],
                total_records=0,
                message="No documents found for this student"
            )
        
        # Generate signed URLs for each document
        file_service = FileService()
        result = []
        
        for doc in documents:
            # Generate signed URL with 1 hour expiry
            doc_url = file_service.get_signed_url(doc.doc_path, 3600)
            
            result.append(StudentDocumentsResponse(
                id=doc.id,
                student_id=doc.student_id,
                document_type=doc.document_type,
                doc_path=doc.doc_path,
                file_name=doc.file_name,
                doc_url=doc_url,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            ))
        
        return StudentDocumentsListResponse(
            data=result,
            total_records=len(result),
            message="Documents retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
