from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.enums import UserType


class UserBase(BaseModel):
    school_id: str = Field(..., description="Unique institution / school ID", min_length=2, max_length=50)
    first_name: str = Field(..., description="First name", min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, description="Middle name (optional)", max_length=100)
    last_name: str = Field(..., description="Last name", min_length=1, max_length=100)
    user_type: UserType = Field(..., description="User role type: student or faculty")


class UserCreate(UserBase):
    id: Optional[UUID] = Field(None, description="UUID matching auth.users(id)")


class UserUpdate(BaseModel):
    school_id: Optional[str] = Field(None, min_length=2, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    user_type: Optional[UserType] = None


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    @property
    def full_name(self) -> str:
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    model_config = ConfigDict(from_attributes=True)
