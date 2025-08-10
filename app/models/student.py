from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy import JSON

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class CasteCategory(str, Enum):
    GENERAL = "General"
    SC = "SC"
    ST = "ST"
    OBC = "OBC"
    MBC = "MBC"
    OTHER = "Other"

class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Student(SQLModel, table=True):
    """Student table for storing student information"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    date_of_birth: datetime = Field(..., description="Date of birth")
    gender: Gender = Field(..., description="Gender")
    address_line1: str = Field(..., description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: str = Field(..., description="City")
    district: str = Field(..., description="District")
    state: str = Field(default="Tamil Nadu", description="State")
    pincode: str = Field(..., description="Pincode")
    parent_name: str = Field(..., description="Parent/Guardian name")
    parent_phone: str = Field(..., description="Parent/Guardian phone")
    parent_email: Optional[str] = Field(None, description="Parent/Guardian email")
    caste_category: CasteCategory = Field(..., description="Caste category")
    annual_income: Optional[float] = Field(None, description="Annual family income")
    minority_status: bool = Field(default=False, description="Minority status")
    physically_challenged: bool = Field(default=False, description="Physically challenged status")
    sports_quota: bool = Field(default=False, description="Sports quota eligibility")
    ncc_quota: bool = Field(default=False, description="NCC quota eligibility")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="students")
    documents: List["StudentDocuments"] = Relationship(back_populates="student")

class StudentDocuments(SQLModel, table=True):
    """Student documents table"""
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    document_type: str = Field(..., description="Type of document")
    doc_path: str = Field(..., description="File path in storage")
    file_name: str = Field(..., description="Original file name")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    student: Student = Relationship(back_populates="documents")

class StudentVerificationStatus(SQLModel, table=True):
    """Student verification status table"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    status: VerificationStatus = Field(default=VerificationStatus.PENDING, description="Verification status")
    remarks: Optional[str] = Field(None, description="Admin remarks")
    verified_by_user_id: Optional[int] = Field(None, description="Admin who verified")
    verified_at: Optional[datetime] = Field(None, description="Verification timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
