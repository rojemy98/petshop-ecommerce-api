from datetime import datetime, UTC
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SCHEMA_NAME


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    stock: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0
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

    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.users.id"),
        nullable=False
    )

    updated_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.users.id"),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name="check_product_price"
        ),
        CheckConstraint(
            "stock >= 0",
            name="check_product_stock"
        ),
    )

    # Relationships

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_products"
    )

    updater = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="updated_products"
    )

    cart_products = relationship(
        "CartProduct",
        back_populates="product"
    )

    invoice_products = relationship(
        "InvoiceProduct",
        back_populates="product"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": float(self.price),
            "stock": self.stock,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            )
        }