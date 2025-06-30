from pydantic import BaseModel, Field


class PlaceCSchema(BaseModel):
    model_config = {
        "str_strip_whitespace": True,
    }
    name: str = Field(
        min_length=1,
        max_length=64,
        title="Place name",
    )
    parent_uid: int | None = Field(
        default=None,
        title="Parent place ID",
    )


class PlaceUSchema(BaseModel):
    model_config = {
        "str_strip_whitespace": True,
    }
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        title="Place name",
    )
    parent_uid: int | None = Field(
        default=None,
        title="Parent place ID",
    )


class PlaceRLSchema(BaseModel):
    uid: int = Field(
        title="Place ID",
    )
    name: str = Field(
        title="Place name",
    )
    parent_uid: int | None = Field(
        default=None,
        title="Parent place ID",
    )


class PlaceRSchema(BaseModel):
    uid: int = Field(
        title="Place ID",
    )
    name: str = Field(
        title="Place name",
    )
    parent: PlaceRLSchema | None = Field(
        default=None,
        title="Parent place",
    )
