from pydantic import BaseModel, EmailStr, Field

# class LoginSchema(BaseModel):
#     email: EmailStr = Field(
#         title="User email",
#     )
#     password: str = Field(
#         max_length=64,
#         title="User password",
#     )


class RegisterSchema(BaseModel):
    model_config = {
        "str_strip_whitespace": True,
    }
    email: EmailStr = Field(
        title="User email",
    )
    password: str = Field(
        min_length=1,
        max_length=64,
        title="User password",
    )


class WithAccessTokenSchema(BaseModel):
    access_token: str = Field(
        title="Access token",
    )


class TokenSchema(WithAccessTokenSchema):
    token_type: str = Field(
        default="bearer",
        title="Token type",
    )


class TokensDTO(WithAccessTokenSchema):
    refresh_token: str = Field(
        title="Refresh token",
    )


class TokenPayloadSchema(BaseModel):
    user_uid: int = Field(
        title="User ID",
    )
