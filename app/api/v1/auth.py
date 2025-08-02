from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserRegister, UserLogin, Token, RefreshToken, 
    UserResponse, PasswordReset, PasswordChange, EmailVerification
)
from app.middleware.auth import get_current_user
from app.models.user import User
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=dict, summary="Register a new user")
async def register(
    user_data: UserRegister,
    session: Session = Depends(get_session)
):
    """
    Register a new user with the following information:
    
    - **email**: User's email address (must be unique)
    - **password**: User's password (minimum 8 characters)
    - **first_name**: User's first name (optional)
    - **last_name**: User's last name (optional)
    - **phone**: User's phone number (optional)
    - **role**: User's role (admin, college, or student)
    
    Returns user information and authentication tokens.
    """
    try:
        auth_service = AuthService(session)
        return auth_service.register_user(user_data)
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise

@router.post("/login", response_model=dict, summary="Login user")
async def login(
    login_data: UserLogin,
    session: Session = Depends(get_session)
):
    """
    Authenticate user and return access tokens.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns user information and authentication tokens.
    """
    try:
        auth_service = AuthService(session)
        return auth_service.login_user(login_data)
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise

@router.post("/refresh", response_model=Token, summary="Refresh access token")
async def refresh_token(
    refresh_data: RefreshToken,
    session: Session = Depends(get_session)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token and refresh token.
    """
    try:
        from app.core.security import verify_token, create_access_token
        
        payload = verify_token(refresh_data.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = int(payload.get("sub"))
        email = payload.get("email")
        role = payload.get("role")
        
        # Verify user still exists and is active
        from sqlmodel import select
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new access token
        access_token = create_access_token(
            data={"sub": str(user_id), "email": email, "role": role}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_data.refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=UserResponse, summary="Get current user information")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    
    Requires valid authentication token.
    """
    return current_user

@router.post("/logout", summary="Logout user")
async def logout():
    """
    Logout user (client should discard tokens).
    
    This endpoint is mainly for documentation purposes.
    The actual logout should be handled by the client by discarding the tokens.
    """
    return {"message": "Successfully logged out"}

@router.post("/password-reset", summary="Request password reset")
async def request_password_reset(
    password_reset: PasswordReset,
    session: Session = Depends(get_session)
):
    """
    Request password reset for a user.
    
    - **email**: Email address for password reset
    
    Sends password reset email if user exists.
    """
    # TODO: Implement email sending functionality
    return {"message": "Password reset email sent (if user exists)"}

@router.post("/password-change", summary="Change password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Change current user's password.
    
    - **current_password**: Current password
    - **new_password**: New password (minimum 8 characters)
    
    Requires valid authentication token.
    """
    try:
        from app.core.security import verify_password, get_password_hash, validate_password_strength
        
        # Verify current password
        if not verify_password(password_change.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password strength
        password_validation = validate_password_strength(password_change.new_password)
        if not password_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password does not meet security requirements"
            )
        
        # Update password
        current_user.password_hash = get_password_hash(password_change.new_password)
        current_user.updated_at = datetime.utcnow()
        
        session.add(current_user)
        session.commit()
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/verify-email", summary="Verify email address")
async def verify_email(
    verification: EmailVerification,
    session: Session = Depends(get_session)
):
    """
    Verify user's email address using verification token.
    
    - **token**: Email verification token
    
    Marks user's email as verified.
    """
    # TODO: Implement email verification functionality
    return {"message": "Email verification endpoint (to be implemented)"} 