import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pydantic import IPvAnyAddress, ValidationError
from sqlalchemy import exists, select
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

ph = PasswordHasher()


JWT_ALGORITHM = "HS256"

INVALID_CREDENTIALS_HTTP_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"msg": "Invalid credentials", "code": "INVALID_CREDENTIALS"},
)

CSRF_TOKEN_MISMATCH_HTTP_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="CSRF token mismatch",
)

REFRESH_COOKIE_KEY = "flea_refresh_token"
CSRF_COOKIE_KEY = "flea_csrf_token"


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
            password=ph.hash(schema.password),
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
            raise INVALID_CREDENTIALS_HTTP_EXCEPTION
        try:
            ph.verify(
                hash=user.password,
                password=schema.password,
            )
        except VerifyMismatchError as exc:
            raise INVALID_CREDENTIALS_HTTP_EXCEPTION from exc
        return user.uid

    async def refresh_token(
        self,
        refresh_token: str,
        csrf_token_header: str,
    ) -> int:
        payload = self.decode_jwt_token(refresh_token)
        session = await self.db_session.scalar(
            select(Session)
            .where(Session.refresh_token == refresh_token)
            .with_for_update(),
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found",
            )
        if payload.user_uid != session.user_uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session",
            )
        if session.csrf_token != csrf_token_header:
            raise CSRF_TOKEN_MISMATCH_HTTP_EXCEPTION
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
        csrf_token = secrets.token_urlsafe(32)
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

        except ValidationError:
            ip = None
        session = Session(
            refresh_token=refresh_token,
            csrf_token=csrf_token,
            user_uid=user_uid,
            ip=ip,
            user_agent=request.headers.get("user-agent"),
        )
        self.db_session.add(session)
        return TokensDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            csrf_token=csrf_token,
        )

    @classmethod
    def apply_user_tokens(
        cls,
        tokens: TokensDTO,
        response: Response,
    ) -> TokenSchema:
        response.set_cookie(
            key=REFRESH_COOKIE_KEY,
            value=tokens.refresh_token,
            httponly=True,
              samesite="lax",
            path="/api/auth/refresh_token/",
        )
        response.set_cookie(
            key=CSRF_COOKIE_KEY,
            value=tokens.csrf_token,
            httponly=False,
            samesite="lax",
            path="/",
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
                "jti": str(uuid4()),
            },
            key=settings.SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

    async def logout(
        self,
        response: Response,
        refresh_token: str,
        csrf_token_header: str,
    ) -> None:
        session = await self.db_session.scalar(
            select(Session).where(Session.refresh_token == refresh_token),
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found",
            )
        if session.csrf_token != csrf_token_header:
            raise CSRF_TOKEN_MISMATCH_HTTP_EXCEPTION
        await self.db_session.delete(session)
        response.delete_cookie(
            key=REFRESH_COOKIE_KEY,
            path="/api/auth/refresh_token/",
        )

    @staticmethod
    def initial_check_tokens(
        refresh_token: str,
        csrf_token_header: str,
        csrf_token_cookie: str,
    ) -> None:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found",
            )
        if csrf_token_header and csrf_token_cookie != csrf_token_header:
            raise CSRF_TOKEN_MISMATCH_HTTP_EXCEPTION
