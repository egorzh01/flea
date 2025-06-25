from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.api import router
from app.config import settings
from app.middlewares.process_time import ProcessTimeMiddleware


@asynccontextmanager
async def lifespan(
    _app: FastAPI,
) -> AsyncGenerator[None]:
    await settings.FILES_PATH.mkdir(exist_ok=True, parents=True)
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    root_path="/api",
)


# __________________________ Middlewares __________________________ #

if settings.MODE != "PROD":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(
    ProcessTimeMiddleware,
)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)

# __________________________ Routers __________________________ #

app.include_router(
    router=router,
)
