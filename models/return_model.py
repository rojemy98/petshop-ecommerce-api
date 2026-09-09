from datetime import datetime, UTC

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SCHEMA_NAME


class Return(Base):
    __tablename__ = "returns"

    id: Mapped[int] = mapped_column(primary_key=True)

    invoice_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.invoices.id"),
        nullable=False
    )

    reason: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="REQUESTED"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        CheckConstraint(
            "status IN "
            "('REQUESTED', 'APPROVED', 'REJECTED', 'COMPLETED')",
            name="check_return_status"
        ),
    )

    invoice = relationship(
        "Invoice",
        back_populates="returns"
    )

    return_products = relationship(
        "ReturnProduct",
        back_populates="return_request",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "invoice_id": self.invoice_id,
            "reason": self.reason,
            "status": self.status,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            ),
            "products": [
                item.to_dict()
                for item in self.return_products
            ]
        }