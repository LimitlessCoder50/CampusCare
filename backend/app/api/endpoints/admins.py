from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from supabase import Client
from app.core.database import get_supabase_admin_client
from app.core.security import require_admin, CurrentUser
from app.schemas.admin import AdminCreate, AdminUpdate, AdminResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admins", tags=["Administrators"])


@router.get(
    "/",
    response_model=List[AdminResponse],
    summary="List administrators with search and pagination",
)
def list_admins(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search term for name, email, or school_id"),
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_admin),
):
    """
    List all administrator profiles. Administrator access required.
    """
    return AdminService.list_admins(admin_client, skip=skip, limit=limit, search=search)


@router.get("/{admin_id}", response_model=AdminResponse, summary="Get administrator by ID")
def get_admin_by_id(
    admin_id: UUID,
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_admin),
):
    """
    Retrieve admin profile by UUID.
    """
    admin = AdminService.get_by_id(admin_client, admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Administrator with ID '{admin_id}' was not found.",
        )
    return admin


@router.get(
    "/by-school-id/{school_id}",
    response_model=AdminResponse,
    summary="Get administrator by school ID",
)
def get_admin_by_school_id(
    school_id: str,
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_admin),
):
    """
    Retrieve admin profile by unique school ID.
    """
    admin = AdminService.get_by_school_id(admin_client, school_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Administrator with school ID '{school_id}' was not found.",
        )
    return admin


@router.post(
    "/",
    response_model=AdminResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create administrator profile directly",
)
def create_admin_profile(
    admin_in: AdminCreate,
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_admin),
):
    """
    Directly create an admin profile in `public.admin`.
    Requires Admin privileges and an existing auth.users ID.
    """
    return AdminService.create_admin(admin_client, admin_in)


@router.put("/{admin_id}", response_model=AdminResponse, summary="Update administrator profile")
def update_admin_profile(
    admin_id: UUID,
    update_in: AdminUpdate,
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_admin),
):
    """
    Update administrator profile details.
    """
    return AdminService.update_admin(admin_client, admin_id, update_in)


@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete administrator profile")
def delete_admin_profile(
    admin_id: UUID,
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_admin),
):
    """
    Delete an admin profile record.
    """
    AdminService.delete_admin(admin_client, admin_id)
    return None
