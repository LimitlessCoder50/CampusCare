from typing import Any, Tuple, Optional
from uuid import UUID
from fastapi import HTTPException, status
from supabase import Client
from app.schemas.enums import AppRole, UserType, EmploymentStatus
from app.schemas.auth import (
    LoginRequest,
    RegisterUserRequest,
    RegisterMaintenanceRequest,
    RegisterAdminRequest,
    AuthResponse,
)
from app.schemas.user import UserCreate, UserResponse
from app.schemas.maintenance import MaintenancePersonnelCreate, MaintenancePersonnelResponse
from app.schemas.admin import AdminCreate, AdminResponse
from app.services.user_service import UserService
from app.services.maintenance_service import MaintenanceService
from app.services.admin_service import AdminService
import logging

logger = logging.getLogger("campuscare.services.auth")


class AuthService:
    @staticmethod
    def resolve_user_profile(
        client: Client, auth_user_id: UUID
    ) -> Tuple[AppRole, Any]:
        """
        Determines which table the auth.users record corresponds to:
        1. public.admin -> admin
        2. public.maintenance_personnel -> maintenance
        3. public.users -> student or faculty (user_type)
        """
        # 1. Check admin
        admin = AdminService.get_by_id(client, auth_user_id)
        if admin:
            return AppRole.admin, admin

        # 2. Check maintenance personnel
        maint = MaintenanceService.get_by_id(client, auth_user_id)
        if maint:
            return AppRole.maintenance, maint

        # 3. Check users (student or faculty)
        user = UserService.get_user_by_id(client, auth_user_id)
        if user:
            role = AppRole.student if user.user_type == UserType.student else AppRole.faculty
            return role, user

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User authentication account exists, but no associated profile was found.",
        )

    @staticmethod
    def register_user(admin_client: Client, req: RegisterUserRequest) -> UserResponse:
        """
        Registers an account in Supabase auth and creates a student/faculty record in public.users.
        """
        auth_user_id = None
        try:
            # 1. Create user in Supabase Auth
            auth_res = admin_client.auth.admin.create_user({
                "email": req.email,
                "password": req.password,
                "email_confirm": True,
                "user_metadata": {
                    "role": req.user_type.value,
                    "first_name": req.first_name,
                    "last_name": req.last_name,
                    "school_id": req.school_id,
                },
            })

            if not auth_res or not auth_res.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create authentication user in Supabase.",
                )

            auth_user_id = auth_res.user.id

            # 2. Insert into public.users
            profile_in = UserCreate(
                id=UUID(auth_user_id),
                school_id=req.school_id,
                first_name=req.first_name,
                middle_name=req.middle_name,
                last_name=req.last_name,
                user_type=req.user_type,
            )
            return UserService.create_user(admin_client, profile_in)

        except Exception as e:
            # Rollback auth user if profile creation failed
            if auth_user_id:
                try:
                    admin_client.auth.admin.delete_user(auth_user_id)
                except Exception as rollback_err:
                    logger.warning(f"Failed to rollback auth user {auth_user_id}: {rollback_err}")
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"Error registering user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(e)}",
            )

    @staticmethod
    def register_maintenance(
        admin_client: Client, req: RegisterMaintenanceRequest
    ) -> MaintenancePersonnelResponse:
        """
        Registers an account in Supabase auth and creates a record in public.maintenance_personnel.
        """
        auth_user_id = None
        try:
            auth_res = admin_client.auth.admin.create_user({
                "email": req.email,
                "password": req.password,
                "email_confirm": True,
                "user_metadata": {
                    "role": "maintenance",
                    "first_name": req.first_name,
                    "last_name": req.last_name,
                    "department": req.department,
                },
            })

            if not auth_res or not auth_res.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create authentication user in Supabase.",
                )

            auth_user_id = auth_res.user.id

            profile_in = MaintenancePersonnelCreate(
                id=UUID(auth_user_id),
                school_id=req.school_id,
                first_name=req.first_name,
                middle_name=req.middle_name,
                last_name=req.last_name,
                email=req.email,
                department=req.department,
                maintenance_category=req.maintenance_category,
                employment_status=EmploymentStatus.pending,
            )
            return MaintenanceService.create_personnel(admin_client, profile_in)

        except Exception as e:
            if auth_user_id:
                try:
                    admin_client.auth.admin.delete_user(auth_user_id)
                except Exception as rollback_err:
                    logger.warning(f"Failed to rollback auth user {auth_user_id}: {rollback_err}")
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"Error registering maintenance personnel: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(e)}",
            )

    @staticmethod
    def register_admin(admin_client: Client, req: RegisterAdminRequest) -> AdminResponse:
        """
        Registers an account in Supabase auth and creates a record in public.admin.
        """
        auth_user_id = None
        try:
            auth_res = admin_client.auth.admin.create_user({
                "email": req.email,
                "password": req.password,
                "email_confirm": True,
                "user_metadata": {
                    "role": "admin",
                    "first_name": req.first_name,
                    "last_name": req.last_name,
                    "school_id": req.school_id,
                },
            })

            if not auth_res or not auth_res.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create authentication user in Supabase.",
                )

            auth_user_id = auth_res.user.id

            profile_in = AdminCreate(
                id=UUID(auth_user_id),
                school_id=req.school_id,
                first_name=req.first_name,
                middle_name=req.middle_name,
                last_name=req.last_name,
                email=req.email,
                password=req.password,
            )
            return AdminService.create_admin(admin_client, profile_in)

        except Exception as e:
            if auth_user_id:
                try:
                    admin_client.auth.admin.delete_user(auth_user_id)
                except Exception as rollback_err:
                    logger.warning(f"Failed to rollback auth user {auth_user_id}: {rollback_err}")
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"Error registering admin: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Admin registration failed: {str(e)}",
            )

    @staticmethod
    def login(
        client: Client, admin_client: Client, credentials: LoginRequest
    ) -> AuthResponse:
        """
        Authenticates against Supabase auth and returns access token + role-specific profile.
        """
        try:
            auth_res = client.auth.sign_in_with_password({
                "email": credentials.email,
                "password": credentials.password,
            })

            if not auth_res or not auth_res.session or not auth_res.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            user_id = UUID(auth_res.user.id)
            role, profile = AuthService.resolve_user_profile(admin_client, user_id)

            return AuthResponse(
                access_token=auth_res.session.access_token,
                refresh_token=auth_res.session.refresh_token,
                token_type="bearer",
                role=role,
                user_id=user_id,
                profile=profile,
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"Login failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {str(e)}",
            )
