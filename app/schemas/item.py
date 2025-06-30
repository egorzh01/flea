from pydantic import BaseModel, Field

from app.models.item import CURRENCY_CODE


class ItemCSchema(BaseModel):
    model_config = {
        "str_strip_whitespace": True,
    }

    name: str = Field(
        min_length=1,
        max_length=64,
        title="Item name",
    )
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=1024,
        title="Item description",
    )
    price: float | None = Field(
        default=None,
        gt=0,
        title="Item price",
    )
    currency_code: CURRENCY_CODE | None = Field(
        default=None,
        title="Item currency",
    )
    quantity: int = Field(
        gt=0,
        title="Item quantity",
    )
    is_public: bool = Field(
        title="Item is public",
    )
    unit_uid: int | None = Field(
        default=None,
        title="Item unit ID",
    )
    place_uid: int | None = Field(
        default=None,
        title="Item place ID",
    )
    category_uid: int | None = Field(
        default=None,
        title="Item category ID",
    )


class ItemUSchema(BaseModel):
    model_config = {
        "str_strip_whitespace": True,
    }

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        title="Item name",
    )
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=1024,
        title="Item description",
    )
    price: float | None = Field(
        default=None,
        gt=0,
        title="Item price",
    )
    currency_code: CURRENCY_CODE | None = Field(
        default=None,
        title="Item currency",
    )
    quantity: int | None = Field(
        default=None,
        gt=0,
        title="Item quantity",
    )
    is_public: bool | None = Field(
        default=None,
        title="Item is public",
    )
    unit_uid: int | None = Field(
        default=None,
        title="Item unit ID",
    )
    place_uid: int | None = Field(
        default=None,
        title="Item place ID",
    )
    category_uid: int | None = Field(
        default=None,
        title="Item category ID",
    )
