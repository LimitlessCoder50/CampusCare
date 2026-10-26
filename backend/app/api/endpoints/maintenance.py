from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from supabase import Client
from app.core.database import get_supabase_admin_client
from app.core.security import require_admin, require_any_user, CurrentUser
from app.schemas.enums import EmploymentStatus
from app.schemas.maintenance import (
    MaintenancePersonnelCreate,
    MaintenancePersonnelUpdate,
    MaintenanceStatusUpdate,
    MaintenancePersonnelResponse,
)
from app.services.maintenance_service import MaintenanceService

router = APIRouter(prefix="/maintenance", tags=["Maintenance Personnel"])


@router.get(
    "/",
    response_model=List[MaintenancePersonnelResponse],
    summary="List maintenance personnel with filters",
)
def list_maintenance(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    department: Optional[str] = Query(None, description="Filter by department"),
    maintenance_category: Optional[str] = Query(None, description="Filter by category (Electrical, Plumbing, etc.)"),
    employment_status: Optional[EmploymentStatus] = Query(None, description="Filter by status (pending, active, inactive)"),
    search: Optional[str] = Query(None, description="Search term for name, email, or school_id"),
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_any_user),
):
    """
    Retrieve a list of maintenance staff, with filters by department, trade category, and employment status.
    """
    return MaintenanceService.list_personnel(
        admin_client,
        skip=skip,
        limit=limit,
        department=department,
        maintenance_category=maintenance_category,
        employment_status=employment_status,
        search=search,
    )


@router.get("/{personnel_id}", response_model=MaintenancePersonnelResponse, summary="Get maintenance staff by ID")
def get_maintenance_by_id(
    personnel_id: UUID,
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_any_user),
):
    """
    Retrieve maintenance personnel by UUID.
    """
    personnel = MaintenanceService.get_by_id(admin_client, personnel_id)
    if not personnel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance personnel with ID '{personnel_id}' was not found.",
        )
    return personnel


@router.post(
    "/",
    response_model=MaintenancePersonnelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create maintenance personnel record directly",
)
def create_maintenance_profile(
    personnel_in: MaintenancePersonnelCreate,
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_admin),
):
    """
    Directly create a maintenance personnel entry. Admin only.
    """
    return MaintenanceService.create_personnel(admin_client, personnel_in)


@router.put("/{personnel_id}", response_model=MaintenancePersonnelResponse, summary="Update maintenance personnel")
def update_maintenance_profile(
    personnel_id: UUID,
    update_in: MaintenancePersonnelUpdate,
    admin_client: Client = Depends(get_supabase_admin_client),
    current_user: CurrentUser = Depends(require_any_user),
):
    """
    Update maintenance staff details. Staff can update their own contact details, or Admin can update any.
    """
    if current_user.role.value != "admin" and current_user.id != personnel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are only permitted to update your own profile.",
        )
    return MaintenanceService.update_personnel(admin_client, personnel_id, update_in)


@router.patch(
    "/{personnel_id}/status",
    response_model=MaintenancePersonnelResponse,
    summary="Update employment status (Approve / Activate / Deactivate)",
)
def update_employment_status(
    personnel_id: UUID,
    status_in: MaintenanceStatusUpdate,
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_admin),
):
    """
    Approve pending personnel or toggle active/inactive status. Administrator only.
    """
    return MaintenanceService.update_status(
        admin_client, personnel_id, status_in.employment_status
    )


@router.delete("/{personnel_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete maintenance personnel")
def delete_maintenance_profile(
    personnel_id: UUID,
    admin_client: Client = Depends(get_supabase_admin_client),
    _: CurrentUser = Depends(require_admin),
):
    """
    Delete a maintenance personnel record from `public.maintenance_personnel`. Administrator only.
    """
    MaintenanceService.delete_personnel(admin_client, personnel_id)
    return None
