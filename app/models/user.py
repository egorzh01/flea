from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class User(Base):
    __tablename__ = "users"

    uid: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="User ID",
    )
    email: Mapped[str] = mapped_column(
        comment="User email",
    )
    password: Mapped[str] = mapped_column(
        comment="User password hash",
    )
