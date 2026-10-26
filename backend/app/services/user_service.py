from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from postgrest.exceptions import APIError
from supabase import Client
from app.schemas.enums import UserType
from app.schemas.user import UserCreate, UserUpdate, UserResponse
import logging

logger = logging.getLogger("campuscare.services.user")


def handle_db_error(e: APIError, entity: str = "User"):
    logger.error(f"Database error on {entity}: {e}")
    # 23505 is PostgreSQL unique_violation
    if getattr(e, "code", None) == "23505":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{entity} with this unique identifier already exists. ({e.message})",
        )
    # 23503 is foreign_key_violation
    if getattr(e, "code", None) == "23503":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Associated auth account does not exist. ({e.message})",
        )
    # 23514 is check_violation
    if getattr(e, "code", None) == "23514":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Field value violates constraints. ({e.message})",
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Database error: {e.message}",
    )


class UserService:
    @staticmethod
    def create_user(client: Client, user_in: UserCreate) -> UserResponse:
        """Create a student or faculty profile in public.users."""
        data = user_in.model_dump(exclude_none=True)
        if "id" in data:
            data["id"] = str(data["id"])

        try:
            res = client.table("users").insert(data).execute()
            if not res.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user record.",
                )
            return UserResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "User")

    @staticmethod
    def get_user_by_id(client: Client, user_id: UUID) -> Optional[UserResponse]:
        """Fetch a user by their UUID."""
        try:
            res = client.table("users").select("*").eq("id", str(user_id)).execute()
            if not res.data:
                return None
            return UserResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "User")

    @staticmethod
    def get_user_by_school_id(client: Client, school_id: str) -> Optional[UserResponse]:
        """Fetch a user by their unique school_id."""
        try:
            res = client.table("users").select("*").eq("school_id", school_id).execute()
            if not res.data:
                return None
            return UserResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "User")

    @staticmethod
    def list_users(
        client: Client,
        skip: int = 0,
        limit: int = 50,
        user_type: Optional[UserType] = None,
        search: Optional[str] = None,
    ) -> List[UserResponse]:
        """List users with filtering by type, search, and pagination."""
        try:
            query = client.table("users").select("*")

            if user_type:
                query = query.eq("user_type", user_type.value)

            if search:
                # Search school_id or last_name or first_name (ilike)
                query = query.or_(
                    f"school_id.ilike.%{search}%,first_name.ilike.%{search}%,last_name.ilike.%{search}%"
                )

            query = query.order("created_at", desc=True).range(skip, skip + limit - 1)
            res = query.execute()
            return [UserResponse(**item) for item in res.data]
        except APIError as e:
            handle_db_error(e, "User")

    @staticmethod
    def update_user(client: Client, user_id: UUID, user_update: UserUpdate) -> UserResponse:
        """Update an existing user profile."""
        update_data = user_update.model_dump(exclude_unset=True)
        if not update_data:
            existing = UserService.get_user_by_id(client, user_id)
            if not existing:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            return existing

        try:
            res = client.table("users").update(update_data).eq("id", str(user_id)).execute()
            if not res.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found or no changes made",
                )
            return UserResponse(**res.data[0])
        except APIError as e:
            handle_db_error(e, "User")

    @staticmethod
    def delete_user(client: Client, user_id: UUID) -> bool:
        """Delete a user profile."""
        try:
            res = client.table("users").delete().eq("id", str(user_id)).execute()
            if not res.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return True
        except APIError as e:
            handle_db_error(e, "User")
