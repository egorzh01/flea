from fastapi import APIRouter

from . import auth

router = APIRouter()

router.include_router(
    router=auth.router,
    prefix="/auth",
)
