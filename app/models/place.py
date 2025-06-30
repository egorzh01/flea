from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Relationship, mapped_column, relationship

from . import Base


class Place(Base):
    __tablename__ = "places"
    __table_args__ = ()

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
            "places.uid",
            ondelete="SET NULL",
            name="places_parent_uid_fkey",
        ),
        default=None,
    )
    owner_uid: Mapped[int] = mapped_column(
        ForeignKey(
            "users.uid",
            ondelete="SET NULL",
            name="places_owner_uid_fkey",
        ),
    )

    parent: Relationship["Place | None"] = relationship(
        back_populates="children",
        remote_side=[uid],
    )
    children: Relationship[list["Place"]] = relationship(
        back_populates="parent",
    )
