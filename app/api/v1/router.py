from fastapi import APIRouter
from app.api.v1 import auth, users, colleges, admin, students, access_control, stages, endpoints

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(colleges.router)
api_router.include_router(admin.router)
api_router.include_router(students.router)
api_router.include_router(access_control.router)
api_router.include_router(stages.router)
api_router.include_router(endpoints.router) 