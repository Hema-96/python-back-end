from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole

# Admin Profile Schemas
class AdminProfileCreate(BaseModel):
    department: Optional[str] = Field(None, max_length=100, description="Admin department")
    permissions: List[str] = Field(default=[], description="Admin permissions")

class AdminProfileResponse(BaseModel):
    id: int
    user_id: int
    department: Optional[str] = None
    permissions: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# College Profile Schemas
class CollegeProfileCreate(BaseModel):
    college_name: str = Field(..., max_length=255, description="College name")
    college_code: str = Field(..., max_length=50, description="College code")
    address: Optional[str] = Field(None, max_length=500, description="College address")
    district: Optional[str] = Field(None, max_length=100, description="District")
    state: str = Field(default="Tamil Nadu", max_length=100, description="State")
    contact_person: Optional[str] = Field(None, max_length=100, description="Contact person")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    website: Optional[str] = Field(None, max_length=255, description="College website")

    @validator('college_code')
    def validate_college_code(cls, v):
        if not v.isalnum():
            raise ValueError('College code must contain only alphanumeric characters')
        return v.upper()

class CollegeProfileResponse(BaseModel):
    id: int
    user_id: int
    college_name: str
    college_code: str
    address: Optional[str] = None
    district: Optional[str] = None
    state: str
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    is_approved: bool
    approved_by_user_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Student Profile Schemas
class StudentProfileCreate(BaseModel):
    date_of_birth: Optional[datetime] = Field(None, description="Date of birth")
    gender: Optional[str] = Field(None, max_length=20, description="Gender")
    address: Optional[str] = Field(None, max_length=500, description="Address")
    district: Optional[str] = Field(None, max_length=100, description="District")
    state: str = Field(default="Tamil Nadu", max_length=100, description="State")
    pincode: Optional[str] = Field(None, max_length=10, description="Pincode")
    parent_name: Optional[str] = Field(None, max_length=100, description="Parent name")
    parent_phone: Optional[str] = Field(None, max_length=20, description="Parent phone")
    caste_category: Optional[str] = Field(None, max_length=50, description="Caste category")
    income_certificate: Optional[str] = Field(None, max_length=255, description="Income certificate")
    community_certificate: Optional[str] = Field(None, max_length=255, description="Community certificate")

    @validator('pincode')
    def validate_pincode(cls, v):
        if v and not v.isdigit() or len(v) != 6:
            raise ValueError('Pincode must be 6 digits')
        return v

class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    state: str
    pincode: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    caste_category: Optional[str] = None
    income_certificate: Optional[str] = None
    community_certificate: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# User Update Schemas
class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")

class UserListResponse(BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True 