from sqlmodel import Session, select
from app.models.user import User, UserRole
from app.models.college import College, CollegeSeatMatrix, CollegeVerificationStatus, VerificationStatus
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self, session: Session):
        self.session = session
    
    def admin_dashboard_tiles(self) -> Dict[str, Any]:
        """
        Get admin dashboard statistics including:
        - Total registered students
        - Approved colleges count
        - Total available seats from approved colleges
        - Current round number
        """
        try:
            # Get total registered students
            student_statement = select(User).where(User.role == UserRole.STUDENT)
            total_students = len(self.session.exec(student_statement).all())
            
            # Get approved colleges count
            approved_colleges_statement = select(College).join(CollegeVerificationStatus).where(
                CollegeVerificationStatus.status == VerificationStatus.APPROVED
            )
            approved_colleges = self.session.exec(approved_colleges_statement).all()
            approved_colleges_count = len(approved_colleges)
            
            # Get total available seats from approved colleges
            total_seats = 0
            for college in approved_colleges:
                seat_matrix_statement = select(CollegeSeatMatrix).where(
                    CollegeSeatMatrix.college_id == college.id
                )
                seat_matrices = self.session.exec(seat_matrix_statement).all()
                
                for seat_matrix in seat_matrices:
                    # Sum up all seat counts from the seat matrix
                    if hasattr(seat_matrix, 'seats') and seat_matrix.seats:
                        try:
                            # If seats is stored as JSON/dict, extract the values
                            if isinstance(seat_matrix.seats, dict):
                                for branch, count in seat_matrix.seats.items():
                                    if isinstance(count, (int, float)):
                                        total_seats += int(count)
                            elif isinstance(seat_matrix.seats, (int, float)):
                                total_seats += int(seat_matrix.seats)
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid seat count format for college {college.id}")
                            continue
            
            # Get current round (you can modify this logic based on your round management)
            current_round = 3  # This could be fetched from a configuration or database
            
            data = [{
                "student": {
                    "label": "Total Registered Students",
                    "value": total_students
                },
                "college": {
                    "label": "Approved Colleges",
                    "value": approved_colleges_count
                },
                "seats": {
                    "label": "Available Seats",
                    "value": total_seats
                },
                "current_round": {
                    "label": "Current Round",
                    "value": current_round
                }
            }]
            
            logger.info(f"Admin dashboard tiles generated: {data}")
            return {"data": data}
            
        except Exception as e:
            logger.error(f"Error generating admin dashboard tiles: {e}")
            raise 