import asyncio
import os

import aiodocker
import asyncpg
import pytest
from alembic import command
from alembic.config import Config
from anyio import Path
from asgi_lifespan import LifespanManager
from faker import Faker
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text

from app.config import settings
from app.database import engine, get_session
from app.main import app
from app.models.user import User

fake = Faker()
variable_pattern = r"{{\s*variables_map\['([^']+)'\]\s*}}"


@pytest.fixture(scope="session", autouse=True)
def check_mode() -> None:
    mode = os.getenv("MODE")
    if mode != "TEST":
        raise PermissionError(
            f"Envrironment variable MODE must be TEST for testing. Current MODE = {mode}",
        )


@pytest.fixture(scope="function", autouse=True)
async def test_dir(tmp_path_factory: pytest.TempPathFactory):
    settings.FILES_PATH = Path(tmp_path_factory.mktemp("files", numbered=True))
    await settings.FILES_PATH.mkdir(exist_ok=True, parents=True)


@pytest.fixture(scope="session", autouse=True)
async def create_db():
    if os.getenv("CI"):
        yield
    else:
        docker = aiodocker.Docker()
        try:
            try:
                await docker.images.inspect("postgres:17-alpine")
            except aiodocker.DockerError:
                await docker.images.pull("postgres:17-alpine")
            # Создаём и запускаем контейнер
            container = await docker.containers.create_or_replace(
                name="test-postgres",
                config={
                    "Image": "postgres:17-alpine",
                    "Env": [
                        f"POSTGRES_USER={settings.POSTGRES_USER}",
                        f"POSTGRES_PASSWORD={settings.POSTGRES_PASSWORD}",
                        f"POSTGRES_DB={settings.POSTGRES_DB}",
                    ],
                    "Ports": {f"{settings.POSTGRES_PORT}/tcp": {}},
                    "HostConfig": {
                        "PortBindings": {
                            "5432/tcp": [{"HostPort": f"{settings.POSTGRES_PORT}"}],
                        },
                    },
                },
            )
            await container.start()

            async def wait_for_db():
                for _ in range(10):
                    try:
                        conn = await asyncpg.connect(
                            user=settings.POSTGRES_USER,
                            password=settings.POSTGRES_PASSWORD,
                            database=settings.POSTGRES_DB,
                            host=settings.POSTGRES_HOST,
                            port=settings.POSTGRES_PORT,
                        )
                        await conn.close()
                        return
                    except ConnectionError:
                        await asyncio.sleep(1)
                raise Exception("PostgreSQL failed to start within the timeout")

            await wait_for_db()
            yield
            await container.stop()
            await container.delete()
        finally:
            await docker.close()


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(create_db: None):
    _ = create_db
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="function", autouse=True)
async def clear_db():
    yield
    async with get_session() as session:
        await session.execute(
            text(
                "TRUNCATE users, documents, document_variables, includes, include_variables, variables, images, images_documents, images_includes, folders, recents, favorites, sessions CASCADE",
            ),
        )
        await session.commit()
    await engine.dispose()


@pytest.fixture()
async def db_session():
    async with get_session() as session:
        yield session


@pytest.fixture()
async def user() -> User:
    async with get_session() as session:
        if user := await session.scalar(select(User)):
            return user
        user = User(
            email="egor@gmail.com",
            password="test_password",
        )
        session.add(user)
        await session.commit()
        return user


@pytest.fixture()
async def client(user: User):
    _ = user
    async with (
        LifespanManager(app, startup_timeout=100, shutdown_timeout=100),
        AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as ac,
    ):
        yield ac
