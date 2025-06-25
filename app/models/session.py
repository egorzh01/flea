from ipaddress import IPv4Address, IPv6Address

from sqlalchemy import DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from app.core.typess import utcdatetime

from . import Base


class Session(Base):
    __tablename__ = "sessions"

    __table_args__ = (
        PrimaryKeyConstraint(
            "refresh_token",
            name="sessions_pkey",
        ),
    )

    refresh_token: Mapped[str] = mapped_column(
        comment="Session ID",
    )
    user_uid: Mapped[int] = mapped_column(
        ForeignKey(
            "users.uid",
            ondelete="CASCADE",
            name="sessions_user_uid_fkey",
        ),
        comment="User ID",
    )
    updated_at: Mapped[utcdatetime] = mapped_column(
        DateTime(timezone=True),
        default=utcdatetime.now,
        onupdate=utcdatetime.now,
        comment="Session last refreshed date",
    )
    ip: Mapped[IPv4Address | IPv6Address | None] = mapped_column(
        INET(),
        default=None,
        comment="IP address",
    )
    user_agent: Mapped[str | None] = mapped_column(
        default=None,
        comment="User agent",
    )
