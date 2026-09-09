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


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.users.id"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'COMPLETED', 'ABANDONED')",
            name="check_cart_status"
        ),
    )

    user = relationship(
        "User",
        back_populates="carts"
    )

    cart_products = relationship(
        "CartProduct",
        back_populates="cart",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
            "products": [
                {
                    "product_id": item.product_id,
                    "name": item.product.name,
                    "quantity": item.quantity,
                    "price_at_added": float(
                        item.price_at_added
                    ),
                    "subtotal": float(
                        item.price_at_added
                        * item.quantity
                    )
                }
                for item in self.cart_products
            ]
        }