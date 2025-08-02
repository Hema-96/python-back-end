from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.user import User, AdminProfile, CollegeProfile, StudentProfile, UserRole
from app.core.security import get_password_hash, verify_password, generate_tokens, validate_password_strength
from app.schemas.auth import UserRegister, UserLogin
from app.schemas.user import AdminProfileCreate, CollegeProfileCreate, StudentProfileCreate
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, session: Session):
        self.session = session

    def register_user(self, user_data: UserRegister) -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Check if user already exists
            statement = select(User).where(User.email == user_data.email)
            existing_user = self.session.exec(statement).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Validate password strength
            password_validation = validate_password_strength(user_data.password)
            if not password_validation["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password does not meet security requirements"
                )

            # Create new user
            hashed_password = get_password_hash(user_data.password)
            user = User(
                email=user_data.email,
                password_hash=hashed_password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone=user_data.phone,
                role=user_data.role,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)

            # Create profile based on role
            if user.role == UserRole.ADMIN:
                admin_profile = AdminProfile(user_id=user.id)
                self.session.add(admin_profile)
            elif user.role == UserRole.STUDENT:
                student_profile = StudentProfile(user_id=user.id)
                self.session.add(student_profile)

            self.session.commit()

            # Generate tokens
            tokens = generate_tokens(user.id, user.email, user.role.value)
            
            logger.info(f"User registered successfully: {user.email}")
            
            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified
                },
                "tokens": tokens
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def login_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        try:
            # Find user by email
            statement = select(User).where(User.email == login_data.email)
            user = self.session.exec(statement).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )

            # Verify password
            if not verify_password(login_data.password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user"
                )

            # Update last login
            user.last_login = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            self.session.add(user)
            self.session.commit()

            # Generate tokens
            tokens = generate_tokens(user.id, user.email, user.role.value)
            
            logger.info(f"User logged in successfully: {user.email}")
            
            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified
                },
                "tokens": tokens
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def create_college_profile(self, user_id: int, profile_data: CollegeProfileCreate) -> CollegeProfile:
        """Create college profile for a user"""
        try:
            # Check if user exists and is a college
            statement = select(User).where(User.id == user_id)
            user = self.session.exec(statement).first()
            
            if not user or user.role != UserRole.COLLEGE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User not found or not a college"
                )

            # Check if college code already exists
            statement = select(CollegeProfile).where(CollegeProfile.college_code == profile_data.college_code)
            existing_college = self.session.exec(statement).first()
            if existing_college:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="College code already exists"
                )

            college_profile = CollegeProfile(
                user_id=user_id,
                college_name=profile_data.college_name,
                college_code=profile_data.college_code,
                address=profile_data.address,
                district=profile_data.district,
                state=profile_data.state,
                contact_person=profile_data.contact_person,
                contact_phone=profile_data.contact_phone,
                website=profile_data.website,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.session.add(college_profile)
            self.session.commit()
            self.session.refresh(college_profile)
            
            logger.info(f"College profile created for user: {user_id}")
            return college_profile
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating college profile: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def create_admin_profile(self, user_id: int, profile_data: AdminProfileCreate) -> AdminProfile:
        """Create admin profile for a user"""
        try:
            # Check if user exists and is an admin
            statement = select(User).where(User.id == user_id)
            user = self.session.exec(statement).first()
            
            if not user or user.role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User not found or not an admin"
                )

            admin_profile = AdminProfile(
                user_id=user_id,
                department=profile_data.department,
                permissions=profile_data.permissions,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.session.add(admin_profile)
            self.session.commit()
            self.session.refresh(admin_profile)
            
            logger.info(f"Admin profile created for user: {user_id}")
            return admin_profile
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating admin profile: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def create_student_profile(self, user_id: int, profile_data: StudentProfileCreate) -> StudentProfile:
        """Create student profile for a user"""
        try:
            # Check if user exists and is a student
            statement = select(User).where(User.id == user_id)
            user = self.session.exec(statement).first()
            
            if not user or user.role != UserRole.STUDENT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User not found or not a student"
                )

            student_profile = StudentProfile(
                user_id=user_id,
                date_of_birth=profile_data.date_of_birth,
                gender=profile_data.gender,
                address=profile_data.address,
                district=profile_data.district,
                state=profile_data.state,
                pincode=profile_data.pincode,
                parent_name=profile_data.parent_name,
                parent_phone=profile_data.parent_phone,
                caste_category=profile_data.caste_category,
                income_certificate=profile_data.income_certificate,
                community_certificate=profile_data.community_certificate,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.session.add(student_profile)
            self.session.commit()
            self.session.refresh(student_profile)
            
            logger.info(f"Student profile created for user: {user_id}")
            return student_profile
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating student profile: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            ) 