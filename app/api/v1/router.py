from fastapi import APIRouter
from app.api.v1 import auth, users

api_router = APIRouter()

# Include all API routers
api_router.include_router(auth.router)
api_router.include_router(users.router) 