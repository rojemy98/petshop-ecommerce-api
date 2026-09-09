from datetime import datetime, UTC

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SCHEMA_NAME


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)

    invoice_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.invoices.id"),
        nullable=False,
        unique=True
    )

    payment_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    payment_reference: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="COMPLETED"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED')",
            name="check_payment_status"
        ),
    )

    invoice = relationship(
        "Invoice",
        back_populates="payment"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "payment_method": self.payment_method,
            "payment_reference": self.payment_reference,
            "status": self.status,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            )
        }