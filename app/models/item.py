from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.item_file import ItemFile
    from app.models.place import Place
    from app.models.tag import Tag
    from app.models.unit import Unit
    from app.models.user import User


class CURRENCY_CODE(str, Enum):
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"
    UAH = "UAH"
    KZT = "KZT"
    BYN = "BYN"
    KGS = "KGS"
    TJS = "TJS"
    UZS = "UZS"
    AZN = "AZN"
    GEL = "GEL"
    AMD = "AMD"
    CNY = "CNY"
    JPY = "JPY"
    KRW = "KRW"
    VND = "VND"
    THB = "THB"


class Item(Base):
    __tablename__ = "items"

    uid: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Item ID",
    )
    name: Mapped[str] = mapped_column(
        comment="Item name",
    )
    description: Mapped[str | None] = mapped_column(
        default=None,
        comment="Item description",
    )
    price: Mapped[float | None] = mapped_column(
        default=None,
        comment="Item price",
    )
    currency_code: Mapped[CURRENCY_CODE | None] = mapped_column(
        default=None,
        comment="Item currency",
    )
    quantity: Mapped[int] = mapped_column(
        comment="Item quantity",
    )
    is_public: Mapped[bool] = mapped_column(
        default=False,
        comment="Item is public",
    )

    category_uid: Mapped[int | None] = mapped_column(
        ForeignKey(
            "categories.uid",
            ondelete="SET NULL",
            name="items_category_uid_fkey",
        ),
        comment="Category ID",
    )
    unit_uid: Mapped[int | None] = mapped_column(
        ForeignKey(
            "units.uid",
            ondelete="RESTRICT",
            name="items_unit_uid_fkey",
        ),
        comment="Unit ID",
    )
    owner_uid: Mapped[int] = mapped_column(
        ForeignKey(
            "users.uid",
            ondelete="CASCADE",
            name="items_owner_uid_fkey",
        ),
        comment="User ID",
    )
    place_uid: Mapped[int | None] = mapped_column(
        ForeignKey(
            "places.uid",
            ondelete="SET NULL",
            name="items_place_uid_fkey",
        ),
        comment="Place ID",
    )

    category: Mapped[Category | None] = relationship(
        back_populates="items",
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary="tags_items",
        back_populates="items",
    )
    unit: Mapped[Unit] = relationship(
        back_populates="items",
    )
    files: Mapped[list[ItemFile]] = relationship(
        back_populates="item",
    )
    owner: Mapped[User] = relationship(
        back_populates="items",
    )
    place: Mapped[Place | None] = relationship(
        back_populates="items",
    )
