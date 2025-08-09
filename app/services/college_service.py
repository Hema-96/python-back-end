from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models.college import (
    College, CollegePrincipal, CollegeSeatMatrix, CollegeFacilities, 
    CollegeDocuments, CollegeBankDetails, CollegeVerificationStatus,
    CollegeType, CounsellingType, VerificationStatus
)
from app.models.user import User, UserRole
from app.schemas.college import CollegeSubmissionSchema
from app.services.file_service import FileService
import logging

logger = logging.getLogger(__name__)

class CollegeService:
    def __init__(self, session: Session):
        self.session = session
        self.file_service = FileService()

    def submit_college_data(self, user_id: int, college_data: CollegeSubmissionSchema) -> Dict[str, Any]:
        """Submit complete college data for verification"""
        try:
            # Check if user is a college admin
            statement = select(User).where(User.id == user_id)
            user = self.session.exec(statement).first()
            if not user or user.role != UserRole.COLLEGE:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only college administrators can submit college data"
                )

            # Check if college code already exists
            statement = select(College).where(College.college_code == college_data.college.college_code)
            existing_college = self.session.exec(statement).first()
            if existing_college:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="College code already exists"
                )

            # Check if user already has a college
            statement = select(College).where(College.user_id == user_id)
            existing_user_college = self.session.exec(statement).first()
            # if existing_user_college:
            #     raise HTTPException(
            #         status_code=status.HTTP_400_BAD_REQUEST,
            #         detail="User already has a college registered"
            #     )

            # Upload logo file if provided
            logo_url = None
            if college_data.college.logo_file:
                logo_upload = self.file_service.upload_file(college_data.college.logo_file, "college-logos")
                logo_url = logo_upload["file_url"]

            # Create college record
            college = College(
                user_id=user_id,  # Link to the user who created it
                college_code=college_data.college.college_code,
                name=college_data.college.name,
                short_name=college_data.college.short_name,
                type=college_data.college.type,
                university_affiliation=college_data.college.university_affiliation,
                year_established=college_data.college.year_established,
                naac_grade=college_data.college.naac_grade,
                nba_status=college_data.college.nba_status,
                aicte_approved=college_data.college.aicte_approved,
                counselling_type=college_data.college.counselling_type,
                address_line1=college_data.college.address.line1,
                address_line2=college_data.college.address.line2,
                city=college_data.college.address.city,
                district=college_data.college.address.district,
                state=college_data.college.address.state,
                pincode=college_data.college.address.pincode,
                phone=college_data.college.contact.phone,
                mobile=college_data.college.contact.mobile,
                email=college_data.college.contact.email,
                website=college_data.college.contact.website,
                logo_url=logo_url,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(college)
            self.session.commit()
            self.session.refresh(college)

            # Upload principal ID proof if provided
            principal_id_proof_url = None
            if college_data.principal.id_proof_file:
                id_proof_upload = self.file_service.upload_file(college_data.principal.id_proof_file, "principal-documents")
                principal_id_proof_url = id_proof_upload["file_url"]

            # Create principal record
            principal = CollegePrincipal(
                college_id=college.id,
                name=college_data.principal.name,
                designation=college_data.principal.designation,
                phone=college_data.principal.phone,
                email=college_data.principal.email,
                id_proof_url=principal_id_proof_url,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(principal)

            # Create seat matrix records
            for seat_data in college_data.seat_matrix:
                seat_matrix = CollegeSeatMatrix(
                    college_id=college.id,
                    course_name=seat_data.course_name,
                    intake_capacity=seat_data.intake_capacity,
                    general_seats=seat_data.general_seats,
                    sc_seats=seat_data.sc_seats,
                    st_seats=seat_data.st_seats,
                    obc_seats=seat_data.obc_seats,
                    minority_seats=seat_data.minority_seats,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.session.add(seat_matrix)

            # Create facilities record
            facilities = CollegeFacilities(
                college_id=college.id,
                hostel_available=college_data.facilities.hostel_available,
                transport_available=college_data.facilities.transport_available,
                wifi_available=college_data.facilities.wifi_available,
                lab_facilities=college_data.facilities.lab_facilities,
                placement_cell=college_data.facilities.placement_cell,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(facilities)

            # Upload and create document records
            for doc_data in college_data.documents:
                # Upload document file
                doc_upload = self.file_service.upload_file(doc_data.doc_file, "college-documents")
                
                document = CollegeDocuments(
                    college_id=college.id,
                    doc_url=doc_upload["file_url"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.session.add(document)

            # Upload cancelled cheque if provided
            cancelled_cheque_url = None
            if college_data.bank_details.cancelled_cheque_file:
                cheque_upload = self.file_service.upload_file(college_data.bank_details.cancelled_cheque_file, "bank-documents")
                cancelled_cheque_url = cheque_upload["file_url"]

            # Create bank details record
            bank_details = CollegeBankDetails(
                college_id=college.id,
                bank_name=college_data.bank_details.bank_name,
                branch=college_data.bank_details.branch,
                account_number=college_data.bank_details.account_number,
                ifsc_code=college_data.bank_details.ifsc_code,
                upi_id=college_data.bank_details.upi_id,
                cancelled_cheque_url=cancelled_cheque_url,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(bank_details)

            # Create verification status record
            verification_status = CollegeVerificationStatus(
                college_id=college.id,
                is_verified=False,
                status=VerificationStatus.PENDING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(verification_status)

            self.session.commit()
            logger.info(f"College data submitted successfully for college: {college.college_code}")
            
            return {
                "message": "College data submitted successfully and pending verification",
                "college_id": college.id,
                "college_code": college.college_code,
                "status": "pending"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error submitting college data: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def get_college_by_id(self, college_id: int) -> Optional[College]:
        """Get college by ID"""
        try:
            statement = select(College).where(College.id == college_id)
            return self.session.exec(statement).first()
        except Exception as e:
            logger.error(f"Error getting college by ID: {e}")
            return None

    def get_colleges_by_user(self, user_id: int) -> List[College]:
        """Get colleges by user ID"""
        try:
            statement = select(College).where(College.user_id == user_id)
            return self.session.exec(statement).all()
        except Exception as e:
            logger.error(f"Error getting colleges by user: {e}")
            return []

    def get_all_colleges(self, skip: int = 0, limit: int = 100) -> List[College]:
        """Get all colleges with pagination"""
        try:
            statement = select(College).offset(skip).limit(limit)
            return self.session.exec(statement).all()
        except Exception as e:
            logger.error(f"Error getting all colleges: {e}")
            return []

    def update_college_verification(self, college_id: int, is_verified: bool, verified_by: int, notes: Optional[str] = None) -> Dict[str, Any]:
        """Update college verification status"""
        try:
            # Get college verification status
            statement = select(CollegeVerificationStatus).where(CollegeVerificationStatus.college_id == college_id)
            verification_status = self.session.exec(statement).first()
            
            if not verification_status:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="College verification status not found"
                )

            # Update verification status
            verification_status.is_verified = is_verified
            verification_status.verified_by = verified_by
            verification_status.verification_notes = notes
            verification_status.status = VerificationStatus.APPROVED if is_verified else VerificationStatus.REJECTED
            verification_status.updated_at = datetime.utcnow()

            self.session.add(verification_status)
            self.session.commit()

            logger.info(f"College verification updated: {college_id}, verified: {is_verified}")
            return {
                "message": "College verification status updated successfully",
                "college_id": college_id,
                "is_verified": is_verified,
                "status": verification_status.status
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating college verification: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            ) 