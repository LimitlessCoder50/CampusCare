from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.schemas.enums import AdminRole


class AdminBase(BaseModel):
    school_id: str = Field(..., description="Administrator School / Staff ID", min_length=2, max_length=50)
    first_name: str = Field(..., description="First name", min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, description="Middle name", max_length=100)
    last_name: str = Field(..., description="Last name", min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Admin email address")
    password: Optional[str] = Field(None, description="Admin password", min_length=6)
    role: AdminRole = Field(default=AdminRole.admin, description="Role identifier (admin)")


class AdminCreate(AdminBase):
    id: Optional[UUID] = Field(None, description="UUID matching auth.users(id)")


class AdminUpdate(BaseModel):
    school_id: Optional[str] = Field(None, min_length=2, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)


class AdminResponse(AdminBase):
    id: UUID
    created_at: datetime

    @property
    def full_name(self) -> str:
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    model_config = ConfigDict(from_attributes=True)
