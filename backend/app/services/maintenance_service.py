from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from postgrest.exceptions import APIError
from supabase import Client
from app.schemas.enums import EmploymentStatus
from app.schemas.maintenance import (
    MaintenancePersonnelCreate,
    MaintenancePersonnelUpdate,
    MaintenancePersonnelResponse,
)
from app.services.user_service import handle_db_error
import logging

logger = logging.getLogger("campuscare.services.maintenance")


class MaintenanceService:
    @staticmethod
    def create_personnel(
        client: Client, personnel_in: MaintenancePersonnelCreate
    ) -> MaintenancePersonnelResponse:
        """Create a maintenance personnel profile in public.maintenance_personnel."""
        data = personnel_in.model_dump(exclude_none=True)
        if "id" in data:
            data["id"] = str(data["id"])

        try:
            res = client.table("maintenance_personnel").insert(data).execute()
            if not res.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create maintenance personnel record.",
                )
            return MaintenancePersonnelResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "Maintenance Personnel")

    @staticmethod
    def get_by_id(client: Client, personnel_id: UUID) -> Optional[MaintenancePersonnelResponse]:
        """Fetch maintenance personnel by their UUID."""
        try:
            res = (
                client.table("maintenance_personnel")
                .select("*")
                .eq("id", str(personnel_id))
                .execute()
            )
            if not res.data:
                return None
            return MaintenancePersonnelResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "Maintenance Personnel")

    @staticmethod
    def get_by_email(client: Client, email: str) -> Optional[MaintenancePersonnelResponse]:
        """Fetch maintenance personnel by email."""
        try:
            res = (
                client.table("maintenance_personnel")
                .select("*")
                .eq("email", email)
                .execute()
            )
            if not res.data:
                return None
            return MaintenancePersonnelResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "Maintenance Personnel")

    @staticmethod
    def get_by_school_id(client: Client, school_id: str) -> Optional[MaintenancePersonnelResponse]:
        """Fetch maintenance personnel by school_id."""
        try:
            res = (
                client.table("maintenance_personnel")
                .select("*")
                .eq("school_id", school_id)
                .execute()
            )
            if not res.data:
                return None
            return MaintenancePersonnelResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "Maintenance Personnel")

    @staticmethod
    def list_personnel(
        client: Client,
        skip: int = 0,
        limit: int = 50,
        department: Optional[str] = None,
        maintenance_category: Optional[str] = None,
        employment_status: Optional[EmploymentStatus] = None,
        search: Optional[str] = None,
    ) -> List[MaintenancePersonnelResponse]:
        """List maintenance personnel with filtering by department, category, status, and search."""
        try:
            query = client.table("maintenance_personnel").select("*")

            if department:
                query = query.eq("department", department)

            if maintenance_category:
                query = query.eq("maintenance_category", maintenance_category)

            if employment_status:
                query = query.eq("employment_status", employment_status.value)

            if search:
                query = query.or_(
                    f"first_name.ilike.%{search}%,last_name.ilike.%{search}%,email.ilike.%{search}%,school_id.ilike.%{search}%"
                )

            query = query.order("created_at", desc=True).range(skip, skip + limit - 1)
            res = query.execute()
            return [MaintenancePersonnelResponse(**item) for item in res.data]
        except APIError as e:
            handle_db_error(e, "Maintenance Personnel")

    @staticmethod
    def update_personnel(
        client: Client, personnel_id: UUID, update_in: MaintenancePersonnelUpdate
    ) -> MaintenancePersonnelResponse:
        """Update maintenance personnel details."""
        update_data = update_in.model_dump(exclude_unset=True)
        if not update_data:
            existing = MaintenanceService.get_by_id(client, personnel_id)
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Maintenance personnel not found",
                )
            return existing

        try:
            res = (
                client.table("maintenance_personnel")
                .update(update_data)
                .eq("id", str(personnel_id))
                .execute()
            )
            if not res.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Maintenance personnel not found or no changes made",
                )
            return MaintenancePersonnelResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "Maintenance Personnel")

    @staticmethod
    def update_status(
        client: Client, personnel_id: UUID, status_val: EmploymentStatus
    ) -> MaintenancePersonnelResponse:
        """Update employment status (e.g., approve pending to active, or deactivate)."""
        try:
            res = (
                client.table("maintenance_personnel")
                .update({"employment_status": status_val.value})
                .eq("id", str(personnel_id))
                .execute()
            )
            if not res.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Maintenance personnel not found",
                )
            return MaintenancePersonnelResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "Maintenance Personnel")

    @staticmethod
    def delete_personnel(client: Client, personnel_id: UUID) -> bool:
        """Delete maintenance personnel profile."""
        try:
            res = (
                client.table("maintenance_personnel")
                .delete()
                .eq("id", str(personnel_id))
                .execute()
            )
            if not res.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Maintenance personnel not found",
                )
            return True
        except APIError as e:
            handle_db_error(e, "Maintenance Personnel")
