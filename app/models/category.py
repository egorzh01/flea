from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Category(Base):
    __tablename__ = "categories"

    uid: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Item ID",
    )
    name: Mapped[str] = mapped_column(
        comment="Item name",
    )
    parent_uid: Mapped[int | None] = mapped_column(
        ForeignKey(
            "categories.uid",
            ondelete="SET NULL",
            name="categories_parent_uid_fkey",
        ),
        default=None,
    )
