from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from app.models.item import Item


class ItemFile(Base):
    __tablename__ = "item_files"

    uid: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="File ID",
    )
    url: Mapped[str] = mapped_column(
        comment="File URL",
    )
    name: Mapped[str] = mapped_column(
        comment="File name",
    )
    extension: Mapped[str] = mapped_column(
        comment="File extension",
    )
    order: Mapped[int] = mapped_column(
        comment="File order",
    )
    item_uid: Mapped[int] = mapped_column(
        ForeignKey(
            "items.uid",
            ondelete="CASCADE",
            name="item_files_item_uid_fkey",
        )
    )

    item: Mapped[Item] = relationship(
        back_populates="files",
    )
