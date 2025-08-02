from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import IntEnum
from sqlalchemy import JSON

class UserRole(IntEnum):
    ADMIN = 1
    COLLEGE = 2
    STUDENT = 3

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    password_hash: str = Field(max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: UserRole = Field(default=UserRole.STUDENT)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    email_verified_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    admin_profile: Optional["AdminProfile"] = Relationship(back_populates="user")
    college_profile: Optional["CollegeProfile"] = Relationship(back_populates="user")
    student_profile: Optional["StudentProfile"] = Relationship(back_populates="user")

class AdminProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    department: Optional[str] = Field(default=None, max_length=100)
    permissions: List[str] = Field(default=[], sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    user: User = Relationship(back_populates="admin_profile")

class CollegeProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    college_name: str = Field(max_length=255)
    college_code: str = Field(unique=True, max_length=50)
    address: Optional[str] = Field(default=None, max_length=500)
    district: Optional[str] = Field(default=None, max_length=100)
    state: str = Field(default="Tamil Nadu", max_length=100)
    contact_person: Optional[str] = Field(default=None, max_length=100)
    contact_phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=255)
    is_approved: bool = Field(default=False)
    approved_by_user_id: Optional[int] = Field(default=None)  # Store as simple integer, not foreign key
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    user: User = Relationship(back_populates="college_profile")

class StudentProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    district: Optional[str] = Field(default=None, max_length=100)
    state: str = Field(default="Tamil Nadu", max_length=100)
    pincode: Optional[str] = Field(default=None, max_length=10)
    parent_name: Optional[str] = Field(default=None, max_length=100)
    parent_phone: Optional[str] = Field(default=None, max_length=20)
    caste_category: Optional[str] = Field(default=None, max_length=50)
    income_certificate: Optional[str] = Field(default=None, max_length=255)
    community_certificate: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    user: User = Relationship(back_populates="student_profile") 