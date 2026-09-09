from datetime import datetime, UTC
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SCHEMA_NAME


class CartProduct(Base):
    __tablename__ = "cart_products"

    id: Mapped[int] = mapped_column(primary_key=True)

    cart_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.carts.id"),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.products.id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    price_at_added: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        UniqueConstraint(
            "cart_id",
            "product_id",
            name="uq_cart_product"
        ),
        CheckConstraint(
            "quantity > 0",
            name="check_cart_product_quantity"
        ),
        CheckConstraint(
            "price_at_added >= 0",
            name="check_cart_product_price"
        ),
    )

    cart = relationship(
        "Cart",
        back_populates="cart_products"
    )

    product = relationship(
        "Product",
        back_populates="cart_products"
    )