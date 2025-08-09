from sqlmodel import Session, select
from app.models.user import User, UserRole, CollegeProfile, StudentProfile
from app.models.college import College, CollegeSeatMatrix, CollegeVerificationStatus, VerificationStatus
from typing import Dict, Any, List
import logging
from datetime import datetime

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
    
    def format_users_for_dashboard(self, users: List[User]) -> List[Dict[str, Any]]:
        """
        Format users for admin dashboard display.
        Returns formatted user data including role, status, and profile information.
        Excludes admin users (role_id != 1) from the results.
        """
        try:
            user_list = []
            for user in users:
                # Skip admin users
                if user.role == UserRole.ADMIN:
                    continue
                # Determine user status
                if not user.is_active:
                    status = "inactive"
                elif user.role == UserRole.COLLEGE:
                    # Check college approval status
                    college_profile = self.session.exec(
                        select(CollegeProfile).where(CollegeProfile.user_id == user.id)
                    ).first()
                    if college_profile and college_profile.is_approved:
                        status = "approved"
                    else:
                        status = "pending"
                elif user.role == UserRole.STUDENT:
                    status = "active" if user.is_active else "inactive"
                else:  # ADMIN
                    status = "active"
                
                # Format last login
                if user.last_login:
                    time_diff = datetime.utcnow() - user.last_login
                    if time_diff.days > 0:
                        last_login = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
                    elif time_diff.seconds > 3600:
                        hours = time_diff.seconds // 3600
                        last_login = f"{hours} hour{'s' if hours > 1 else ''} ago"
                    elif time_diff.seconds > 60:
                        minutes = time_diff.seconds // 60
                        last_login = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
                    else:
                        last_login = "Just now"
                else:
                    last_login = "Never"
                
                # Get role name
                role_names = {
                    UserRole.ADMIN: "admin",
                    UserRole.COLLEGE: "college", 
                    UserRole.STUDENT: "student"
                }
                role_name = role_names.get(user.role, "unknown")
                
                # Get institution name for colleges
                institution = None
                if user.role == UserRole.COLLEGE:
                    college_profile = self.session.exec(
                        select(CollegeProfile).where(CollegeProfile.user_id == user.id)
                    ).first()
                    if college_profile:
                        institution = college_profile.college_name
                
                # Format registration date
                registration_date = user.created_at.strftime("%Y-%m-%d") if user.created_at else None
                
                # Build user data
                user_data = {
                    "id": str(user.id),
                    "name": f"{user.first_name or ''} {user.last_name or ''}".strip() or "N/A",
                    "email": user.email,
                    "role": role_name,
                    "status": status,
                    "lastLogin": last_login,
                    "registrationDate": registration_date,
                    "phone": user.phone or "N/A"
                }
                
                # Add institution for colleges
                if institution:
                    user_data["institution"] = institution
                
                user_list.append(user_data)
            
            logger.info(f"Formatted {len(user_list)} users for dashboard")
            return user_list
            
        except Exception as e:
            logger.error(f"Error formatting users for dashboard: {e}")
            raise
    
