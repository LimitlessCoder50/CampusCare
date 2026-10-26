from fastapi import APIRouter, Depends, status
from supabase import Client
from app.core.database import get_supabase_client, get_supabase_admin_client
from app.core.security import get_current_user
from app.schemas.auth import (
    LoginRequest,
    RegisterUserRequest,
    RegisterMaintenanceRequest,
    RegisterAdminRequest,
    AuthResponse,
    CurrentUser,
)
from app.schemas.user import UserResponse
from app.schemas.maintenance import MaintenancePersonnelResponse
from app.schemas.admin import AdminResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=AuthResponse, summary="Log in with email and password")
def login(
    credentials: LoginRequest,
    client: Client = Depends(get_supabase_client),
    admin_client: Client = Depends(get_supabase_admin_client),
):
    """
    Authenticate against Supabase Auth using email and password.
    Returns JWT access_token, user role, and complete profile data.
    """
    return AuthService.login(client, admin_client, credentials)


@router.post(
    "/register/user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a student or faculty account",
)
def register_user(
    req: RegisterUserRequest,
    admin_client: Client = Depends(get_supabase_admin_client),
):
    """
    Registers a new student or faculty account in Supabase Auth and inserts
    the corresponding profile into the `public.users` table.
    """
    return AuthService.register_user(admin_client, req)


@router.post(
    "/register/maintenance",
    response_model=MaintenancePersonnelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register maintenance personnel account",
)
def register_maintenance(
    req: RegisterMaintenanceRequest,
    admin_client: Client = Depends(get_supabase_admin_client),
):
    """
    Registers a new maintenance personnel account in Supabase Auth and inserts
    the profile into the `public.maintenance_personnel` table with pending status.
    """
    return AuthService.register_maintenance(admin_client, req)


@router.post(
    "/register/admin",
    response_model=AdminResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register an administrator account",
)
def register_admin(
    req: RegisterAdminRequest,
    admin_client: Client = Depends(get_supabase_admin_client),
):
    """
    Registers a new administrator account in Supabase Auth and inserts
    the profile into the `public.admin` table.
    """
    return AuthService.register_admin(admin_client, req)


@router.get("/me", response_model=CurrentUser, summary="Get current authenticated user")
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """
    Retrieve profile details and role of the currently logged-in user.
    """
    return current_user
