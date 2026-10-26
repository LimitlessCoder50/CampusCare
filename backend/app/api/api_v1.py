from fastapi import APIRouter
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.users import router as users_router
from app.api.endpoints.maintenance import router as maintenance_router
from app.api.endpoints.admins import router as admins_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(maintenance_router)
api_router.include_router(admins_router)
