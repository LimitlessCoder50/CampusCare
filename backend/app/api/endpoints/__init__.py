from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.users import router as users_router
from app.api.endpoints.maintenance import router as maintenance_router
from app.api.endpoints.admins import router as admins_router

__all__ = ["auth_router", "users_router", "maintenance_router", "admins_router"]
