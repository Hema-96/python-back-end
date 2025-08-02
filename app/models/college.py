from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CounsellingType(str, Enum):
    UG = "UG"
    PG = "PG"
    DIPLOMA = "Diploma"

class CollegeType(str, Enum):
    GOVERNMENT = "Government"
    PRIVATE = "Private"
    AIDED = "Aided"
    SELF_FINANCING = "Self Financing"

class VerificationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class College(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", description="User who created this college (role == 2)")
    college_code: str = Field(unique=True, max_length=20, index=True)
    name: str = Field(max_length=255)
    short_name: Optional[str] = Field(default=None, max_length=50)
    type: CollegeType = Field(default=CollegeType.PRIVATE)
    university_affiliation: Optional[str] = Field(default=None, max_length=255)
    year_established: Optional[int] = None
    naac_grade: Optional[str] = Field(default=None, max_length=10)
    nba_status: bool = Field(default=False)
    aicte_approved: bool = Field(default=False)
    counselling_type: CounsellingType = Field(default=CounsellingType.UG)
    address_line1: Optional[str] = Field(default=None)
    address_line2: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None, max_length=100)
    district: Optional[str] = Field(default=None, max_length=100)
    state: str = Field(default="Tamil Nadu", max_length=100)
    pincode: Optional[str] = Field(default=None, max_length=10)
    phone: Optional[str] = Field(default=None, max_length=15)
    mobile: Optional[str] = Field(default=None, max_length=15)
    email: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None)
    logo_url: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="colleges")
    principal: Optional["CollegePrincipal"] = Relationship(back_populates="college")
    seat_matrix: List["CollegeSeatMatrix"] = Relationship(back_populates="college")
    facilities: Optional["CollegeFacilities"] = Relationship(back_populates="college")
    documents: List["CollegeDocuments"] = Relationship(back_populates="college")
    bank_details: Optional["CollegeBankDetails"] = Relationship(back_populates="college")
    verification_status: Optional["CollegeVerificationStatus"] = Relationship(back_populates="college")

class CollegePrincipal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    college_id: int = Field(foreign_key="college.id")
    name: str = Field(max_length=255)
    designation: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=15)
    email: Optional[str] = Field(default=None, max_length=100)
    id_proof_url: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    college: College = Relationship(back_populates="principal")

class CollegeSeatMatrix(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    college_id: int = Field(foreign_key="college.id")
    course_name: str = Field(max_length=100)
    intake_capacity: int = Field(gt=0)
    general_seats: int = Field(ge=0)
    sc_seats: int = Field(ge=0)
    st_seats: int = Field(ge=0)
    obc_seats: int = Field(ge=0)
    minority_seats: int = Field(ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    college: College = Relationship(back_populates="seat_matrix")

class CollegeFacilities(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    college_id: int = Field(foreign_key="college.id", unique=True)
    hostel_available: bool = Field(default=False)
    transport_available: bool = Field(default=False)
    wifi_available: bool = Field(default=False)
    lab_facilities: Optional[str] = Field(default=None)
    placement_cell: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    college: College = Relationship(back_populates="facilities")

class CollegeDocuments(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    college_id: int = Field(foreign_key="college.id")
    doc_type: str = Field(max_length=100)
    doc_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    college: College = Relationship(back_populates="documents")

class CollegeBankDetails(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    college_id: int = Field(foreign_key="college.id", unique=True)
    bank_name: str = Field(max_length=255)
    branch: Optional[str] = Field(default=None, max_length=100)
    account_number: str = Field(max_length=50)
    ifsc_code: str = Field(max_length=20)
    upi_id: Optional[str] = Field(default=None, max_length=100)
    cancelled_cheque_url: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    college: College = Relationship(back_populates="bank_details")

class CollegeVerificationStatus(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    college_id: int = Field(foreign_key="college.id", unique=True)
    is_verified: bool = Field(default=False)
    verified_by: Optional[int] = Field(foreign_key="user.id", default=None)
    verification_notes: Optional[str] = Field(default=None)
    rejected_reason: Optional[str] = Field(default=None)
    status: VerificationStatus = Field(default=VerificationStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    college: College = Relationship(back_populates="verification_status") 