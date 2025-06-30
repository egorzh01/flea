from fastapi import APIRouter

from . import auth, places

router = APIRouter()

router.include_router(
    router=auth.router,
    prefix="/auth",
)

router.include_router(
    router=places.router,
    prefix="/places",
)
