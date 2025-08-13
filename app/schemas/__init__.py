from .auth import *
from .user import *
from .college import *
from .student import *
from .access_control import *

__all__ = [
    # Auth schemas
    "Token", "TokenData", "UserLogin", "UserRegister", "UserResponse",
    "PasswordChange", "RefreshToken", "EmailVerification",
    
    # User schemas
    "AdminProfileCreate", "AdminProfileResponse",
    "CollegeProfileCreate", "CollegeProfileResponse",
    "StudentProfileCreate", "StudentProfileResponse",
    "UserUpdate", "UserListResponse",
    
    # College schemas
    "CollegeSubmissionSchema", "CollegeResponse", "CollegeListResponse",
    "CollegeVerificationResponse", "CollegeBasicInfo", "AddressSchema", "ContactSchema",
    "PrincipalSchema", "SeatMatrixSchema", "FacilitiesSchema", "DocumentSchema", "BankDetailsSchema",
    "CollegeDocumentsResponse", "CollegeDocumentsListResponse",
    
    # Student schemas
    "StudentSubmissionSchema", "StudentResponse", "StudentListResponse",
    "StudentVerificationResponse", "StudentPersonalInfo", "StudentAcademicInfo", "StudentDocumentSchema", "StudentDocumentUploadSchema",
    "StudentDocumentsResponse", "StudentDocumentsListResponse",
    "Gender", "CasteCategory",
    
    # Access Control schemas
    "PermissionBase", "PermissionCreate", "PermissionUpdate", "PermissionResponse",
    "RoleBase", "RoleCreate", "RoleUpdate", "RoleResponse",
    "RolePermissionBase", "RolePermissionCreate", "RolePermissionUpdate", "RolePermissionResponse",
    "UserRoleAssignmentBase", "UserRoleAssignmentCreate", "UserRoleAssignmentUpdate", "UserRoleAssignmentResponse",
    "EndpointAccessBase", "EndpointAccessCreate", "EndpointAccessUpdate", "EndpointAccessResponse",
    "AccessLogBase", "AccessLogCreate", "AccessLogResponse",
    "SessionLogBase", "SessionLogCreate", "SessionLogResponse",
    
    # Stage Management schemas
    "StageBase", "StageCreate", "StageUpdate", "StageResponse",
    "StagePermissionBase", "StagePermissionCreate", "StagePermissionUpdate", "StagePermissionResponse",
    "CurrentStageResponse"
] 