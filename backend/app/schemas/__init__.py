from app.schemas.enums import UserType, EmploymentStatus, AdminRole, AppRole
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.maintenance import (
    MaintenancePersonnelBase,
    MaintenancePersonnelCreate,
    MaintenancePersonnelUpdate,
    MaintenanceStatusUpdate,
    MaintenancePersonnelResponse,
)
from app.schemas.admin import AdminBase, AdminCreate, AdminUpdate, AdminResponse
from app.schemas.auth import (
    LoginRequest,
    RegisterUserRequest,
    RegisterMaintenanceRequest,
    RegisterAdminRequest,
    AuthResponse,
    CurrentUser,
)

__all__ = [
    "UserType",
    "EmploymentStatus",
    "AdminRole",
    "AppRole",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "MaintenancePersonnelBase",
    "MaintenancePersonnelCreate",
    "MaintenancePersonnelUpdate",
    "MaintenanceStatusUpdate",
    "MaintenancePersonnelResponse",
    "AdminBase",
    "AdminCreate",
    "AdminUpdate",
    "AdminResponse",
    "LoginRequest",
    "RegisterUserRequest",
    "RegisterMaintenanceRequest",
    "RegisterAdminRequest",
    "AuthResponse",
    "CurrentUser",
]
