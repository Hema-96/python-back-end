from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from fastapi import UploadFile
from app.models.college import CollegeType, CounsellingType, VerificationStatus

# Address Schema
class AddressSchema(BaseModel):
    line1: str = Field(..., description="Address line 1")
    line2: Optional[str] = Field(None, description="Address line 2")
    city: str = Field(..., max_length=100, description="City")
    district: str = Field(..., max_length=100, description="District")
    state: str = Field(default="Tamil Nadu", max_length=100, description="State")
    pincode: str = Field(..., max_length=10, description="Pincode")

    @validator('pincode')
    def validate_pincode(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Pincode must be 6 digits')
        return v

# Contact Schema
class ContactSchema(BaseModel):
    phone: Optional[str] = Field(None, max_length=15, description="Phone number")
    mobile: str = Field(..., max_length=15, description="Mobile number")
    email: str = Field(..., max_length=100, description="Email address")
    website: Optional[str] = Field(None, description="Website URL")

    @validator('mobile')
    def validate_mobile(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError('Mobile number must be 10 digits')
        return v

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v

# College Basic Info Schema
class CollegeBasicInfo(BaseModel):
    college_code: str = Field(..., max_length=20, description="Unique college code")
    name: str = Field(..., max_length=255, description="College name")
    short_name: Optional[str] = Field(None, max_length=50, description="Short name")
    type: CollegeType = Field(default=CollegeType.PRIVATE, description="College type")
    university_affiliation: Optional[str] = Field(None, max_length=255, description="University affiliation")
    year_established: Optional[int] = Field(None, ge=1900, le=2024, description="Year established")
    naac_grade: Optional[str] = Field(None, max_length=10, description="NAAC grade")
    nba_status: bool = Field(default=False, description="NBA status")
    aicte_approved: bool = Field(default=False, description="AICTE approval status")
    counselling_type: CounsellingType = Field(default=CounsellingType.UG, description="Counselling type")
    address: AddressSchema
    contact: ContactSchema
    logo_file: Optional[UploadFile] = Field(None, description="College logo file")

    @validator('college_code')
    def validate_college_code(cls, v):
        if not v.isalnum():
            raise ValueError('College code must contain only alphanumeric characters')
        return v.upper()

# Principal Schema
class PrincipalSchema(BaseModel):
    name: str = Field(..., max_length=255, description="Principal name")
    designation: Optional[str] = Field(None, max_length=100, description="Designation")
    phone: Optional[str] = Field(None, max_length=15, description="Phone number")
    email: str = Field(..., max_length=100, description="Email address")
    id_proof_file: Optional[UploadFile] = Field(None, description="ID proof document file")

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v

# Seat Matrix Schema
class SeatMatrixSchema(BaseModel):
    course_name: str = Field(..., max_length=100, description="Course name")
    intake_capacity: int = Field(..., gt=0, description="Total intake capacity")
    general_seats: int = Field(..., ge=0, description="General category seats")
    sc_seats: int = Field(..., ge=0, description="SC category seats")
    st_seats: int = Field(..., ge=0, description="ST category seats")
    obc_seats: int = Field(..., ge=0, description="OBC category seats")
    minority_seats: int = Field(..., ge=0, description="Minority category seats")

    @validator('intake_capacity')
    def validate_intake_capacity(cls, v, values):
        if 'general_seats' in values and 'sc_seats' in values and 'st_seats' in values and 'obc_seats' in values and 'minority_seats' in values:
            total_seats = values['general_seats'] + values['sc_seats'] + values['st_seats'] + values['obc_seats'] + values['minority_seats']
            if total_seats != v:
                raise ValueError('Sum of all category seats must equal intake capacity')
        return v

# Facilities Schema
class FacilitiesSchema(BaseModel):
    hostel_available: bool = Field(default=False, description="Hostel availability")
    transport_available: bool = Field(default=False, description="Transport availability")
    wifi_available: bool = Field(default=False, description="WiFi availability")
    lab_facilities: Optional[str] = Field(None, description="Laboratory facilities")
    placement_cell: bool = Field(default=False, description="Placement cell availability")

# Document Schema
class DocumentSchema(BaseModel):
    doc_file: UploadFile = Field(..., description="Document file")
    file_name: Optional[str] = Field(None, description="Original file name")

# Bank Details Schema
class BankDetailsSchema(BaseModel):
    bank_name: str = Field(..., max_length=255, description="Bank name")
    branch: Optional[str] = Field(None, max_length=100, description="Branch name")
    account_number: str = Field(..., max_length=50, description="Account number")
    ifsc_code: str = Field(..., max_length=20, description="IFSC code")
    upi_id: Optional[str] = Field(None, max_length=100, description="UPI ID")
    cancelled_cheque_file: Optional[UploadFile] = Field(None, description="Cancelled cheque file")

    @validator('account_number')
    def validate_account_number(cls, v):
        if not v.isdigit() or len(v) < 9 or len(v) > 18:
            raise ValueError('Account number must be 9-18 digits')
        return v

    @validator('ifsc_code')
    def validate_ifsc_code(cls, v):
        if len(v) != 11 or not v[:4].isalpha() or not v[4:].isalnum():
            raise ValueError('IFSC code must be 11 characters: 4 letters + 7 alphanumeric')
        return v.upper()

# Complete College Submission Schema
class CollegeSubmissionSchema(BaseModel):
    college: CollegeBasicInfo
    principal: PrincipalSchema
    seat_matrix: List[SeatMatrixSchema] = Field(..., min_items=1, description="Seat matrix for courses")
    facilities: FacilitiesSchema
    documents: List[DocumentSchema] = Field(..., min_items=1, description="Required documents")
    bank_details: BankDetailsSchema

# Response Schemas
class CollegeResponse(BaseModel):
    id: int
    college_code: str
    name: str
    short_name: Optional[str] = None
    type: CollegeType
    university_affiliation: Optional[str] = None
    year_established: Optional[int] = None
    naac_grade: Optional[str] = None
    nba_status: bool
    aicte_approved: bool
    counselling_type: CounsellingType
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: str
    pincode: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CollegeVerificationResponse(BaseModel):
    id: int
    college_id: int
    is_verified: bool
    verified_by: Optional[int] = None
    verification_notes: Optional[str] = None
    rejected_reason: Optional[str] = None
    status: VerificationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CollegeListResponse(BaseModel):
    id: int
    college_code: str
    name: str
    type: CollegeType
    city: Optional[str] = None
    district: Optional[str] = None
    status: VerificationStatus
    numeric_status: int = Field(..., description="Numeric status: 1=Pending, 2=Approved, 3=Rejected")
    created_at: datetime

    class Config:
        from_attributes = True

class CollegeDocumentsResponse(BaseModel):
    id: int
    college_id: int
    doc_path: str
    file_name: str
    doc_url: Optional[str] = Field(None, description="Signed URL for document access")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CollegeDocumentsListResponse(BaseModel):
    data: List[CollegeDocumentsResponse] = Field(..., description="List of college documents")
    total_records: int = Field(..., description="Total number of documents")
    message: str = Field(default="Documents retrieved successfully", description="Response message")

    class Config:
        from_attributes = True 