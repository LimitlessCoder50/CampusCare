from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from supabase import Client
from app.core.database import get_supabase_admin_client
from app.core.security import require_admin, require_any_user, CurrentUser
from app.schemas.enums import UserType
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users (Students & Faculty)"])


@router.get("/", response_model=List[UserResponse], summary="List users with optional filters")
def list_users(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    user_type: Optional[UserType] = Query(None, description="Filter by user type: student or faculty"),
    search: Optional[str] = Query(None, description="Search term for name or school_id"),
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_any_user),
):
    """
    Retrieve a paginated list of users (students and faculty).
    Supports filtering by user_type and text searching.
    """
    return UserService.list_users(
        admin_client, skip=skip, limit=limit, user_type=user_type, search=search
    )


@router.get("/by-school-id/{school_id}", response_model=UserResponse, summary="Get user by school ID")
def get_user_by_school_id(
    school_id: str,
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_any_user),
):
    """
    Find a student or faculty member by their unique school ID.
    """
    user = UserService.get_user_by_school_id(admin_client, school_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with school ID '{school_id}' was not found.",
        )
    return user


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by UUID")
def get_user_by_id(
    user_id: UUID,
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_any_user),
):
    """
    Retrieve user profile by primary key UUID.
    """
    user = UserService.get_user_by_id(admin_client, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' was not found.",
        )
    return user


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user profile directly",
)
def create_user_profile(
    user_in: UserCreate,
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_admin),
):
    """
    Directly insert a profile into `public.users`.
    Requires Admin privileges and an existing auth.users ID.
    """
    return UserService.create_user(admin_client, user_in)


@router.put("/{user_id}", response_model=UserResponse, summary="Update user profile")
def update_user_profile(
    user_id: UUID,
    user_in: UserUpdate,
    admin_client: Client = Depends(get_supabase_admin_client),
    current_user: CurrentUser = Depends(require_any_user),
):
    """
    Update user profile. Users can update their own profile, or admins can update any profile.
    """
    if current_user.role.value != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are only permitted to update your own profile.",
        )
    return UserService.update_user(admin_client, user_id, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user profile")
def delete_user_profile(
    user_id: UUID,
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_admin),
):
    """
    Delete a user profile record from `public.users`. Admin privileges required.
    """
    UserService.delete_user(admin_client, user_id)
    return None
