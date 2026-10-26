from functools import lru_cache
from typing import Optional
from fastapi import HTTPException, status
from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger("campuscare.database")


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get the standard Supabase client initialized with the public anon key.
    Used for public or user-scoped queries respecting RLS.
    """
    try:
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Supabase client initialization failed: {str(e)}",
        )


@lru_cache()
def get_supabase_admin_client() -> Client:
    """
    Get the admin Supabase client initialized with the SERVICE_ROLE_KEY.
    Bypasses Row-Level Security (RLS) for backend operations like creating profiles,
    managing users, and assigning maintenance staff.
    """
    try:
        key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
        return create_client(settings.SUPABASE_URL, key)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase admin client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Supabase admin client initialization failed: {str(e)}",
        )


def get_user_scoped_client(access_token: str) -> Client:
    """
    Get a Supabase client authenticated on behalf of a specific user token.
    This ensures RLS policies on tables evaluate `auth.uid() = user_id`.
    """
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    client.postgrest.auth(access_token)
    return client
