from fastapi import APIRouter
from . import accidents

api_router = APIRouter()
api_router.include_router(accidents.router, prefix="/accidents", tags=["accidents"])