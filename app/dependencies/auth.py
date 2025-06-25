from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from pydantic_core import ValidationError

from app.config import settings


class Auth(BaseModel):
    user_uid: int = Field(
        title="User ID",
    )


async def get_auth(
    token: Annotated[
        str,
        Depends(OAuth2PasswordBearer(tokenUrl="/api/auth/login/")),
    ],
) -> Auth:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        auth = Auth.model_validate(payload)
    except (jwt.InvalidTokenError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    return auth


AuthDep = Annotated[Auth, Depends(get_auth)]
