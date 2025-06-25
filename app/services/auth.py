from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pydantic import IPvAnyAddress, ValidationError
from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.session import Session
from app.models.user import User
from app.schemas.auth import (
    RegisterSchema,
    TokenPayloadSchema,
    TokenSchema,
    TokensDTO,
)

JWT_ALGORITHM = "HS256"

INCORRECT_CREDENTIALS_HTTP_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect credentials",
)


class AuthService:
    def __init__(
        self,
        db_session: AsyncSession,
    ) -> None:
        self.db_session = db_session

    async def register(
        self,
        schema: RegisterSchema,
    ) -> int:
        stmt = select(exists().where(User.email == schema.email))
        if await self.db_session.scalar(stmt):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        user = User(
            email=schema.email,
            password=bcrypt.hashpw(
                password=schema.password.encode("utf-8"),
                salt=bcrypt.gensalt(),
            ).decode("utf-8"),
        )
        self.db_session.add(user)
        await self.db_session.flush()
        return user.uid

    async def login(
        self,
        schema: OAuth2PasswordRequestForm,
    ) -> int:
        stmt = select(User).where(User.email == schema.username)
        user = await self.db_session.scalar(stmt)
        if not user:
            raise INCORRECT_CREDENTIALS_HTTP_EXCEPTION
        if not bcrypt.checkpw(
            password=schema.password.encode("utf-8"),
            hashed_password=user.password.encode("utf-8"),
        ):
            raise INCORRECT_CREDENTIALS_HTTP_EXCEPTION
        return user.uid

    async def refresh_token(
        self,
        refresh_token: str,
    ) -> int:
        self.decode_jwt_token(refresh_token)
        session = await self.db_session.scalar(
            select(Session).where(Session.refresh_token == refresh_token),
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found",
            )
        await self.db_session.delete(session)
        return session.user_uid

    async def create_session(
        self,
        user_uid: int,
        request: Request,
    ) -> TokensDTO:
        payload = TokenPayloadSchema(
            user_uid=user_uid,
        )
        access_token = self.create_jwt_token(payload, timedelta(minutes=15))
        refresh_token = self.create_jwt_token(payload, timedelta(days=30))
        x_forwarded_for = request.headers.get("x-forwarded-for")
        try:
            ip = IPvAnyAddress(  # type: ignore
                (
                    x_forwarded_for.split(",")[0]
                    if x_forwarded_for
                    else request.client.host
                    if request.client
                    else ""
                ).strip(),
            )

        except Exception:
            ip = None
        session = Session(
            refresh_token=refresh_token,
            user_uid=user_uid,
            ip=ip,
            user_agent=request.headers.get("user-agent"),
        )
        self.db_session.add(session)
        return TokensDTO(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    @classmethod
    def apply_user_tokens(
        cls,
        tokens: TokensDTO,
        response: Response,
    ) -> TokenSchema:
        response.set_cookie(
            key="flea_refresh_token",
            value=tokens.refresh_token,
            httponly=True,
            samesite="strict",
            path="/api/auth/refresh_token/",
        )
        return TokenSchema(
            access_token=tokens.access_token,
            token_type="bearer",
        )

    @staticmethod
    def decode_jwt_token(
        token: str,
    ) -> TokenPayloadSchema:
        try:
            data = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[JWT_ALGORITHM],
            )
            return TokenPayloadSchema.model_validate(data)
        except (InvalidTokenError, ValidationError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from e

    @staticmethod
    def create_jwt_token(
        payload: TokenPayloadSchema,
        exp: timedelta,
    ) -> str:
        return jwt.encode(
            payload={
                "exp": datetime.now(UTC) + exp,
                **payload.model_dump(by_alias=True),
            },
            key=settings.SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

    async def logout(
        self,
        response: Response,
        refresh_token: str,
    ) -> None:
        await self.db_session.execute(
            delete(Session).where(Session.refresh_token == refresh_token),
        )
        response.delete_cookie(
            key="docsbox_refresh_token",
            path="/api/auth/refresh_token/",
        )
