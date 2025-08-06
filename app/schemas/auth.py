from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")

class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    first_name: Optional[str] = Field(None, max_length=100, description="User first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User last name")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")
    role: UserRole = Field(default=UserRole.STUDENT, description="User role")

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PasswordReset(BaseModel):
    email: EmailStr = Field(..., description="Email address for password reset")

class PasswordChange(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v

class RefreshToken(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")

class EmailVerification(BaseModel):
    token: str = Field(..., description="Email verification token")

class SetNewPassword(BaseModel):
    email: str = Field(..., description="User's email address")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)") 