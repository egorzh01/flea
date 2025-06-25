from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_DSN, echo=False)
get_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with get_session() as session:
        yield session


DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@asynccontextmanager
async def safe_commit(db_session: AsyncSession) -> AsyncIterator[None]:
    try:
        yield
        await db_session.commit()
    except Exception:
        await db_session.rollback()
        raise
