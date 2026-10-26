from typing import Optional, Union, Any, Dict
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.schemas.enums import UserType, EmploymentStatus, AppRole
from app.schemas.user import UserResponse
from app.schemas.maintenance import MaintenancePersonnelResponse
from app.schemas.admin import AdminResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Account password (min 6 chars)")
    school_id: str = Field(..., min_length=2, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    user_type: UserType = Field(..., description="student or faculty")


class RegisterMaintenanceRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    school_id: Optional[str] = Field(None, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    maintenance_category: Optional[str] = Field(None, max_length=100)


class RegisterAdminRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    school_id: str = Field(..., min_length=2, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    role: AppRole
    user_id: UUID
    profile: Union[UserResponse, MaintenancePersonnelResponse, AdminResponse, Dict[str, Any]]


class CurrentUser(BaseModel):
    id: UUID
    email: Optional[EmailStr] = None
    role: AppRole
    profile: Union[UserResponse, MaintenancePersonnelResponse, AdminResponse, Dict[str, Any]]
