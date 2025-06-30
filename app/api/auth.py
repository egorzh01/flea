from typing import Annotated

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Header,
    Request,
    Response,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from app.database import DBSessionDep, safe_commit
from app.schemas.auth import RegisterSchema, TokenSchema
from app.services.auth import (
    CSRF_COOKIE_KEY,
    REFRESH_COOKIE_KEY,
    AuthService,
)

router = APIRouter(
    tags=["auth"],
)




@router.post(
    path="/login/",
    status_code=status.HTTP_200_OK,
    response_model=TokenSchema,
)
async def login(
    schema: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: DBSessionDep,
    request: Request,
    response: Response,
) -> TokenSchema:
    service = AuthService(db_session=db_session)
    user_uid = await service.login(schema)
    async with safe_commit(db_session):
        tokens = await service.create_session(
            user_uid=user_uid,
            request=request,
        )
    return service.apply_user_tokens(
        tokens=tokens,
        response=response,
    )


@router.post(
    path="/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=TokenSchema,
)
async def register(
    schema: RegisterSchema,
    db_session: DBSessionDep,
    request: Request,
    response: Response,
) -> TokenSchema:
    service = AuthService(db_session=db_session)
    async with safe_commit(db_session):
        user_uid = await service.register(schema)
        tokens = await service.create_session(
            user_uid=user_uid,
            request=request,
        )
    return service.apply_user_tokens(
        tokens=tokens,
        response=response,
    )


@router.post(
    path="/refresh_token/",
    status_code=status.HTTP_200_OK,
    response_model=TokenSchema,
)
async def refresh_token(  # noqa: PLR0913
    db_session: DBSessionDep,
    request: Request,
    response: Response,
    refresh_token: Annotated[str, Cookie(alias=REFRESH_COOKIE_KEY)] = "",
    csrf_token_cookie: Annotated[str, Cookie(alias=CSRF_COOKIE_KEY)] = "",
    csrf_token_header: Annotated[str, Header(alias="X-CSRF-Token")] = "",
) -> TokenSchema:
    AuthService.initial_check_tokens(
        refresh_token=refresh_token,
        csrf_token_header=csrf_token_header,
        csrf_token_cookie=csrf_token_cookie,
    )
    service = AuthService(db_session=db_session)
    async with safe_commit(db_session):
        user_uid = await service.refresh_token(
            refresh_token=refresh_token,
            csrf_token_header=csrf_token_header,
        )
        tokens = await service.create_session(
            user_uid=user_uid,
            request=request,
        )
    return service.apply_user_tokens(
        tokens=tokens,
        response=response,
    )


@router.delete(
    path="/refresh_token/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    response: Response,
    db_session: DBSessionDep,
    refresh_token: Annotated[str, Cookie(alias=REFRESH_COOKIE_KEY)] = "",
    csrf_token_header: Annotated[str, Header(alias="X-CSRF-Token")] = "",
    csrf_token_cookie: Annotated[str, Cookie(alias=CSRF_COOKIE_KEY)] = "",
) -> None:
    AuthService.initial_check_tokens(
        refresh_token=refresh_token,
        csrf_token_header=csrf_token_header,
        csrf_token_cookie=csrf_token_cookie,
    )
    service = AuthService(db_session=db_session)
    async with safe_commit(db_session):
        await service.logout(
            response=response,
            refresh_token=refresh_token,
            csrf_token_header=csrf_token_header,
        )
