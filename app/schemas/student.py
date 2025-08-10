from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

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

class StudentSubmissionSchema(BaseModel):
    """Complete student data submission schema"""
    personal_info: "StudentPersonalInfo"
    academic_info: "StudentAcademicInfo"
    documents: List["StudentDocumentUploadSchema"]

class StudentPersonalInfo(BaseModel):
    """Student personal information"""
    date_of_birth: datetime = Field(..., description="Date of birth")
    gender: Gender = Field(..., description="Gender")
    address_line1: str = Field(..., description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: str = Field(..., description="City")
    district: str = Field(..., description="District")
    state: str = Field(default="Tamil Nadu", description="State")
    pincode: str = Field(..., description="Pincode")
    
    @validator('pincode')
    def validate_pincode(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Pincode must be 6 digits')
        return v

class StudentAcademicInfo(BaseModel):
    """Student academic information"""
    parent_name: str = Field(..., description="Parent/Guardian name")
    parent_phone: str = Field(..., description="Parent/Guardian phone")
    parent_email: Optional[str] = Field(None, description="Parent/Guardian email")
    caste_category: CasteCategory = Field(..., description="Caste category")
    annual_income: Optional[float] = Field(None, description="Annual family income")
    minority_status: bool = Field(default=False, description="Minority status")
    physically_challenged: bool = Field(default=False, description="Physically challenged status")
    sports_quota: bool = Field(default=False, description="Sports quota eligibility")
    ncc_quota: bool = Field(default=False, description="NCC quota eligibility")

class StudentDocumentSchema(BaseModel):
    """Student document schema"""
    document_type: str = Field(..., description="Type of document")
    document_file: Optional[str] = Field(None, description="Document file path")
    file_name: Optional[str] = Field(None, description="Document file name")

class StudentDocumentUploadSchema(BaseModel):
    """Student document upload schema for API requests"""
    document_type: str = Field(..., description="Type of document")
    document_file: Optional[str] = Field(None, description="Document file path")
    file_name: Optional[str] = Field(None, description="Document file name")

class StudentResponse(BaseModel):
    """Student response schema"""
    id: int
    user_id: int
    date_of_birth: datetime
    gender: Gender
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    district: str
    state: str
    pincode: str
    parent_name: str
    parent_phone: str
    parent_email: Optional[str] = None
    caste_category: CasteCategory
    annual_income: Optional[float] = None
    minority_status: bool
    physically_challenged: bool
    sports_quota: bool
    ncc_quota: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudentListResponse(BaseModel):
    """Student list response schema"""
    id: int
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    date_of_birth: datetime
    gender: Gender
    district: str
    caste_category: CasteCategory
    created_at: datetime
    numeric_status: int = Field(..., description="Verification status: 1=Pending, 2=Approved, 3=Rejected")

    class Config:
        from_attributes = True

class StudentVerificationResponse(BaseModel):
    """Student verification response schema"""
    id: int
    user_id: int
    status: str = Field(..., description="Verification status")
    remarks: Optional[str] = Field(None, description="Admin remarks")
    verified_by_user_id: Optional[int] = Field(None, description="Admin who verified")
    verified_at: Optional[datetime] = Field(None, description="Verification timestamp")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudentDocumentsResponse(BaseModel):
    """Student document response schema"""
    id: int
    student_id: int
    document_type: str
    doc_path: str
    file_name: str
    doc_url: Optional[str] = Field(None, description="Signed URL for document access")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudentDocumentsListResponse(BaseModel):
    """Student documents list response schema"""
    data: List[StudentDocumentsResponse] = Field(..., description="List of student documents")
    total_records: int = Field(..., description="Total number of documents")
    message: str = Field(default="Documents retrieved successfully", description="Response message")

    class Config:
        from_attributes = True
