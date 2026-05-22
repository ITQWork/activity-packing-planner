from fastapi import APIRouter
from app.api.v1.endpoints import auth, trips, activities, items, categories

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(trips.router, prefix="/trips", tags=["trips"])
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
