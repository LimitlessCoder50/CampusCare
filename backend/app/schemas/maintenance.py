from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.schemas.enums import EmploymentStatus


class MaintenancePersonnelBase(BaseModel):
    school_id: Optional[str] = Field(None, description="Employee school/staff ID", max_length=50)
    first_name: Optional[str] = Field(None, description="First name", max_length=100)
    middle_name: Optional[str] = Field(None, description="Middle name", max_length=100)
    last_name: Optional[str] = Field(None, description="Last name", max_length=100)
    email: Optional[EmailStr] = Field(None, description="Official email address")
    department: Optional[str] = Field(None, description="Department (e.g., Physical Plant, IT, Facilities)", max_length=100)
    maintenance_category: Optional[str] = Field(None, description="Specialty category (e.g., Electrical, Plumbing, HVAC, Carpentry)", max_length=100)
    employment_status: EmploymentStatus = Field(default=EmploymentStatus.pending, description="Employment status: pending, active, inactive")


class MaintenancePersonnelCreate(MaintenancePersonnelBase):
    id: Optional[UUID] = Field(None, description="UUID matching auth.users(id)")


class MaintenancePersonnelUpdate(BaseModel):
    school_id: Optional[str] = Field(None, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=100)
    maintenance_category: Optional[str] = Field(None, max_length=100)
    employment_status: Optional[EmploymentStatus] = None


class MaintenanceStatusUpdate(BaseModel):
    employment_status: EmploymentStatus = Field(..., description="Updated employment status")


class MaintenancePersonnelResponse(MaintenancePersonnelBase):
    id: UUID
    created_at: datetime

    @property
    def full_name(self) -> str:
        parts = [p for p in [self.first_name, self.middle_name, self.last_name] if p]
        return " ".join(parts) if parts else "Personnel"

    model_config = ConfigDict(from_attributes=True)
