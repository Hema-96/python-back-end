from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models.college import (
    College, CollegePrincipal, CollegeSeatMatrix, CollegeFacilities,
    CollegeDocuments, CollegeBankDetails, CollegeVerificationStatus,
    VerificationStatus
)
from app.models.user import User, UserRole
from app.schemas.college import (
    CollegeSubmissionSchema, CollegeResponse, CollegeListResponse,
    CollegeVerificationResponse
)
import logging

logger = logging.getLogger(__name__)

class CollegeService:
    def __init__(self, session: Session):
        self.session = session

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
            if existing_user_college:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already has a college registered"
                )

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
                logo_url=college_data.college.logo_url,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(college)
            self.session.commit()
            self.session.refresh(college)

            # Create principal record
            principal = CollegePrincipal(
                college_id=college.id,
                name=college_data.principal.name,
                designation=college_data.principal.designation,
                phone=college_data.principal.phone,
                email=college_data.principal.email,
                id_proof_url=college_data.principal.id_proof_url,
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

            # Create document records
            for doc_data in college_data.documents:
                document = CollegeDocuments(
                    college_id=college.id,
                    doc_type=doc_data.doc_type,
                    doc_url=doc_data.doc_url,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.session.add(document)

            # Create bank details record
            bank_details = CollegeBankDetails(
                college_id=college.id,
                bank_name=college_data.bank_details.bank_name,
                branch=college_data.bank_details.branch,
                account_number=college_data.bank_details.account_number,
                ifsc_code=college_data.bank_details.ifsc_code,
                upi_id=college_data.bank_details.upi_id,
                cancelled_cheque_url=college_data.bank_details.cancelled_cheque_url,
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

    def get_college_by_user(self, user_id: int) -> Optional[College]:
        """Get college data for a specific user"""
        try:
            statement = select(College).where(College.user_id == user_id)
            college = self.session.exec(statement).first()
            return college
            
        except Exception as e:
            logger.error(f"Error getting college for user {user_id}: {e}")
            return None

    def get_college_details(self, college_id: int) -> Optional[Dict[str, Any]]:
        """Get complete college details including all related data"""
        try:
            # Get college basic info
            statement = select(College).where(College.id == college_id)
            college = self.session.exec(statement).first()
            if not college:
                return None

            # Get principal
            statement = select(CollegePrincipal).where(CollegePrincipal.college_id == college_id)
            principal = self.session.exec(statement).first()

            # Get seat matrix
            statement = select(CollegeSeatMatrix).where(CollegeSeatMatrix.college_id == college_id)
            seat_matrix = self.session.exec(statement).all()

            # Get facilities
            statement = select(CollegeFacilities).where(CollegeFacilities.college_id == college_id)
            facilities = self.session.exec(statement).first()

            # Get documents
            statement = select(CollegeDocuments).where(CollegeDocuments.college_id == college_id)
            documents = self.session.exec(statement).all()

            # Get bank details
            statement = select(CollegeBankDetails).where(CollegeBankDetails.college_id == college_id)
            bank_details = self.session.exec(statement).first()

            # Get verification status
            statement = select(CollegeVerificationStatus).where(CollegeVerificationStatus.college_id == college_id)
            verification_status = self.session.exec(statement).first()

            return {
                "college": college,
                "principal": principal,
                "seat_matrix": seat_matrix,
                "facilities": facilities,
                "documents": documents,
                "bank_details": bank_details,
                "verification_status": verification_status
            }

        except Exception as e:
            logger.error(f"Error getting college details for college {college_id}: {e}")
            return None

    def get_all_colleges(self, skip: int = 0, limit: int = 20, status: Optional[VerificationStatus] = None) -> List[Dict[str, Any]]:
        """Get all colleges with optional filtering"""
        try:
            statement = select(College).join(CollegeVerificationStatus)
            
            if status:
                statement = statement.where(CollegeVerificationStatus.status == status)
            
            statement = statement.offset(skip).limit(limit)
            colleges = self.session.exec(statement).all()
            
            result = []
            for college in colleges:
                # Get verification status for each college
                v_status = self.session.exec(
                    select(CollegeVerificationStatus).where(CollegeVerificationStatus.college_id == college.id)
                ).first()
                
                result.append({
                    "college": college,
                    "verification_status": v_status
                })
            
            return result

        except Exception as e:
            logger.error(f"Error getting all colleges: {e}")
            return []

    def verify_college(self, college_id: int, admin_user_id: int, is_approved: bool, notes: Optional[str] = None, rejected_reason: Optional[str] = None) -> Dict[str, Any]:
        """Verify or reject a college (admin only)"""
        try:
            # Check if admin user exists
            statement = select(User).where(User.id == admin_user_id)
            admin_user = self.session.exec(statement).first()
            if not admin_user or admin_user.role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only administrators can verify colleges"
                )

            # Get verification status
            statement = select(CollegeVerificationStatus).where(CollegeVerificationStatus.college_id == college_id)
            verification_status = self.session.exec(statement).first()
            
            if not verification_status:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="College verification status not found"
                )

            # Update verification status
            verification_status.is_verified = is_approved
            verification_status.verified_by = admin_user_id
            verification_status.verification_notes = notes
            verification_status.rejected_reason = rejected_reason
            verification_status.status = VerificationStatus.APPROVED if is_approved else VerificationStatus.REJECTED
            verification_status.updated_at = datetime.utcnow()

            self.session.add(verification_status)
            self.session.commit()

            logger.info(f"College {college_id} {'approved' if is_approved else 'rejected'} by admin {admin_user_id}")
            
            return {
                "message": f"College {'approved' if is_approved else 'rejected'} successfully",
                "college_id": college_id,
                "status": verification_status.status,
                "verified_by": admin_user_id
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying college {college_id}: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            ) 