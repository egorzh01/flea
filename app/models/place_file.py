from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from app.models.place import Place


class PlaceFile(Base):
    __tablename__ = "place_files"

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
    place_uid: Mapped[int] = mapped_column(
        ForeignKey(
            "places.uid",
            ondelete="CASCADE",
            name="place_files_place_uid_fkey",
        )
    )
    place: Mapped[Place] = relationship(
        back_populates="files",
    )
