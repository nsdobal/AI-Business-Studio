from fastapi import APIRouter

from app.api.v1.controllers import auth_controller, health_controller

api_router = APIRouter()
api_router.include_router(health_controller.router)
api_router.include_router(auth_controller.router)
