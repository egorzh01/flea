from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Unit(Base):
    __tablename__ = "units"

    uid: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Item ID",
    )
    code: Mapped[str] = mapped_column(
        unique=True,
        comment="Item code",
    )
    name: Mapped[str] = mapped_column(
        comment="Item name",
    )
    short_name: Mapped[str] = mapped_column(
        comment="Item short name",
    )
