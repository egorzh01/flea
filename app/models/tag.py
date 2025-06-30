from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Tag(Base):
    __tablename__ = "tags"

    uid: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Item ID",
    )
    name: Mapped[str] = mapped_column(
        comment="Item name",
    )
    owner_uid: Mapped[int] = mapped_column(
        ForeignKey(
            "users.uid",
            ondelete="CASCADE",
            name="tags_owner_uid_fkey",
        )
    )
