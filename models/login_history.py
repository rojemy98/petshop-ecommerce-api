from datetime import datetime, UTC

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    String
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SCHEMA_NAME


class LoginHistory(Base):
    __tablename__ = "login_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.users.id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False
    )

    success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="login_history"
    )