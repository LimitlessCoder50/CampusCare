from typing import Optional, List
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from supabase import Client
from app.core.config import settings
from app.core.database import get_supabase_client, get_supabase_admin_client
from app.schemas.enums import AppRole
from app.schemas.auth import CurrentUser
from app.services.auth_service import AuthService
import logging

logger = logging.getLogger("campuscare.security")

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    client: Client = Depends(get_supabase_client),
    admin_client: Client = Depends(get_supabase_admin_client),
) -> CurrentUser:
    """
    Validates Supabase Bearer token, retrieves auth identity,
    and resolves the user's role and database profile.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Step 1: Verify token with Supabase Auth or decode payload
    user_id = None
    user_email = None

    try:
        # Check via Supabase Auth server
        user_res = client.auth.get_user(token)
        if user_res and user_res.user:
            user_id = UUID(user_res.user.id)
            user_email = user_res.user.email
    except Exception as auth_err:
        logger.debug(f"Supabase auth get_user failed, attempting local decode: {auth_err}")

    # Fallback to local decode if JWT secret is configured
    if not user_id:
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            sub = payload.get("sub")
            if not sub:
                raise ValueError("Token missing sub claim")
            user_id = UUID(sub)
            user_email = payload.get("email")
        except Exception as jwt_err:
            logger.error(f"JWT validation failed: {jwt_err}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Step 2: Resolve profile from public tables
    role, profile = AuthService.resolve_user_profile(admin_client, user_id)

    return CurrentUser(
        id=user_id,
        email=user_email,
        role=role,
        profile=profile,
    )


class RoleChecker:
    """
    FastAPI dependency factory to enforce role-based access control (RBAC).
    """

    def __init__(self, allowed_roles: List[AppRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: User has role '{current_user.role.value}', but requires one of {[r.value for r in self.allowed_roles]}.",
            )
        return current_user


# Role dependency helpers
require_admin = RoleChecker([AppRole.admin])
require_maintenance = RoleChecker([AppRole.maintenance, AppRole.admin])
require_student_or_faculty = RoleChecker([AppRole.student, AppRole.faculty, AppRole.admin])
require_any_user = RoleChecker([AppRole.admin, AppRole.maintenance, AppRole.student, AppRole.faculty])
