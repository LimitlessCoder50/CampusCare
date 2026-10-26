from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from postgrest.exceptions import APIError
from supabase import Client
from app.schemas.admin import AdminCreate, AdminUpdate, AdminResponse
from app.services.user_service import handle_db_error
import logging

logger = logging.getLogger("campuscare.services.admin")


class AdminService:
    @staticmethod
    def create_admin(client: Client, admin_in: AdminCreate) -> AdminResponse:
        """Create an administrator profile in public.admin."""
        data = admin_in.model_dump(exclude_none=True)
        if "id" in data:
            data["id"] = str(data["id"])

        try:
            res = client.table("admin").insert(data).execute()
            if not res.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create admin record.",
                )
            return AdminResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "Admin")

    @staticmethod
    def get_by_id(client: Client, admin_id: UUID) -> Optional[AdminResponse]:
        """Fetch admin by UUID."""
        try:
            res = client.table("admin").select("*").eq("id", str(admin_id)).execute()
            if not res.data:
                return None
            return AdminResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "Admin")

    @staticmethod
    def get_by_email(client: Client, email: str) -> Optional[AdminResponse]:
        """Fetch admin by email."""
        try:
            res = client.table("admin").select("*").eq("email", email).execute()
            if not res.data:
                return None
            return AdminResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "Admin")

    @staticmethod
    def get_by_school_id(client: Client, school_id: str) -> Optional[AdminResponse]:
        """Fetch admin by school_id."""
        try:
            res = client.table("admin").select("*").eq("school_id", school_id).execute()
            if not res.data:
                return None
            return AdminResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "Admin")

    @staticmethod
    def list_admins(
        client: Client,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
    ) -> List[AdminResponse]:
        """List admins with search and pagination."""
        try:
            query = client.table("admin").select("*")

            if search:
                query = query.or_(
                    f"first_name.ilike.%{search}%,last_name.ilike.%{search}%,email.ilike.%{search}%,school_id.ilike.%{search}%"
                )

            query = query.order("created_at", desc=True).range(skip, skip + limit - 1)
            res = query.execute()
            return [AdminResponse(**item) for item in res.data]
        except APIError as e:
            handle_db_error(e, "Admin")

    @staticmethod
    def update_admin(client: Client, admin_id: UUID, update_in: AdminUpdate) -> AdminResponse:
        """Update admin profile details."""
        update_data = update_in.model_dump(exclude_unset=True)
        if not update_data:
            existing = AdminService.get_by_id(client, admin_id)
            if not existing:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
            return existing

        try:
            res = client.table("admin").update(update_data).eq("id", str(admin_id)).execute()
            if not res.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Admin not found or no changes made",
                )
            return AdminResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "Admin")

    @staticmethod
    def delete_admin(client: Client, admin_id: UUID) -> bool:
        """Delete an admin profile."""
        try:
            res = client.table("admin").delete().eq("id", str(admin_id)).execute()
            if not res.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Admin not found",
                )
            return True
        except APIError as e:
            handle_db_error(e, "Admin")
