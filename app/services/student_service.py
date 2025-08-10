from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from app.models.student import Student, StudentDocuments, StudentVerificationStatus, VerificationStatus
from app.models.user import User
from app.schemas.student import StudentSubmissionSchema, StudentResponse, StudentListResponse
from app.services.file_service import FileService
from fastapi import HTTPException, status, UploadFile

logger = logging.getLogger(__name__)

class StudentService:
    def __init__(self, session: Session):
        self.session = session
        self.file_service = FileService()

    def submit_student_data(self, user_id: int, student_data: StudentSubmissionSchema, document_files: List[UploadFile]) -> Dict[str, Any]:
        """Submit student data for verification"""
        try:
            # Check if student already exists
            existing_student = self.session.exec(
                select(Student).where(Student.user_id == user_id)
            ).first()
            
            if existing_student:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Student data already submitted"
                )

            # Create student record
            student = Student(
                user_id=user_id,
                date_of_birth=student_data.personal_info.date_of_birth,
                gender=student_data.personal_info.gender,
                address_line1=student_data.personal_info.address_line1,
                address_line2=student_data.personal_info.address_line2,
                city=student_data.personal_info.city,
                district=student_data.personal_info.district,
                state=student_data.personal_info.state,
                pincode=student_data.personal_info.pincode,
                parent_name=student_data.academic_info.parent_name,
                parent_phone=student_data.academic_info.parent_phone,
                parent_email=student_data.academic_info.parent_email,
                caste_category=student_data.academic_info.caste_category,
                annual_income=student_data.academic_info.annual_income,
                minority_status=student_data.academic_info.minority_status,
                physically_challenged=student_data.academic_info.physically_challenged,
                sports_quota=student_data.academic_info.sports_quota,
                ncc_quota=student_data.academic_info.ncc_quota
            )
            
            self.session.add(student)
            self.session.commit()
            self.session.refresh(student)

            # Process and store documents
            for doc_file in document_files:
                # Upload file to storage
                file_result = self.file_service.upload_file(doc_file)
                
                # Create document record
                document = StudentDocuments(
                    student_id=student.id,
                    document_type="Document",  # Default document type
                    doc_path=file_result["file_path"],  # Extract the file path string from the dictionary
                    file_name=doc_file.filename or "document"
                )
                
                self.session.add(document)

            # Create verification status record
            verification_status = StudentVerificationStatus(
                user_id=user_id,
                status=VerificationStatus.PENDING
            )
            
            self.session.add(verification_status)
            self.session.commit()

            return {
                "message": "Student data submitted successfully",
                "student_id": student.id,
                "status": "PENDING"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error submitting student data: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def get_student_by_user_id(self, user_id: int) -> Optional[Student]:
        """Get student by user ID"""
        return self.session.exec(
            select(Student).where(Student.user_id == user_id)
        ).first()

    def get_all_students(self, skip: int = 0, limit: int = 20) -> List[StudentListResponse]:
        """Get all students with pagination"""
        students = self.session.exec(
            select(Student, User)
            .join(User, Student.user_id == User.id)
            .offset(skip)
            .limit(limit)
        ).all()
        
        result = []
        for student, user in students:
            # Get verification status
            verification = self.session.exec(
                select(StudentVerificationStatus).where(StudentVerificationStatus.user_id == student.user_id)
            ).first()
            
            numeric_status = 1  # Default to pending
            if verification:
                if verification.status == VerificationStatus.APPROVED:
                    numeric_status = 2
                elif verification.status == VerificationStatus.REJECTED:
                    numeric_status = 3
            
            result.append(StudentListResponse(
                id=student.id,
                user_id=student.user_id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                date_of_birth=student.date_of_birth,
                gender=student.gender,
                district=student.district,
                caste_category=student.caste_category,
                created_at=student.created_at,
                numeric_status=numeric_status
            ))
        
        return result

    def get_pending_students(self, skip: int = 0, limit: int = 20) -> List[StudentListResponse]:
        """Get pending students with pagination"""
        pending_verifications = self.session.exec(
            select(StudentVerificationStatus)
            .where(StudentVerificationStatus.status == VerificationStatus.PENDING)
            .offset(skip)
            .limit(limit)
        ).all()
        
        result = []
        for verification in pending_verifications:
            student = self.session.exec(
                select(Student).where(Student.user_id == verification.user_id)
            ).first()
            
            if student:
                user = self.session.exec(
                    select(User).where(User.id == verification.user_id)
                ).first()
                
                result.append(StudentListResponse(
                    id=student.id,
                    user_id=student.user_id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    date_of_birth=student.date_of_birth,
                    gender=student.gender,
                    district=student.district,
                    caste_category=student.caste_category,
                    created_at=student.created_at,
                    numeric_status=1
                ))
        
        return result

    def get_approved_students(self, skip: int = 0, limit: int = 20) -> List[StudentListResponse]:
        """Get approved students with pagination"""
        approved_verifications = self.session.exec(
            select(StudentVerificationStatus)
            .where(StudentVerificationStatus.status == VerificationStatus.APPROVED)
            .offset(skip)
            .limit(limit)
        ).all()
        
        result = []
        for verification in approved_verifications:
            student = self.session.exec(
                select(Student).where(Student.user_id == verification.user_id)
            ).first()
            
            if student:
                user = self.session.exec(
                    select(User).where(User.id == verification.user_id)
                ).first()
                
                result.append(StudentListResponse(
                    id=student.id,
                    user_id=student.user_id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    date_of_birth=student.date_of_birth,
                    gender=student.gender,
                    district=student.district,
                    caste_category=student.caste_category,
                    created_at=student.created_at,
                    numeric_status=2
                ))
        
        return result

    def update_student_verification(self, user_id: int, status: VerificationStatus, remarks: Optional[str] = None, verified_by_user_id: Optional[int] = None) -> Dict[str, Any]:
        """Update student verification status"""
        try:
            verification = self.session.exec(
                select(StudentVerificationStatus).where(StudentVerificationStatus.user_id == user_id)
            ).first()
            
            if not verification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Student verification record not found"
                )
            
            verification.status = status
            verification.remarks = remarks
            verification.verified_by_user_id = verified_by_user_id
            verification.verified_at = datetime.utcnow()
            verification.updated_at = datetime.utcnow()
            
            self.session.add(verification)
            self.session.commit()
            
            return {
                "message": f"Student verification status updated to {status}",
                "user_id": user_id,
                "status": status
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating student verification: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
