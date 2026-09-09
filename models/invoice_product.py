from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Numeric
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SCHEMA_NAME


class InvoiceProduct(Base):
    __tablename__ = "invoice_products"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.products.id"),
        nullable=False
    )

    invoice_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.invoices.id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="check_invoice_product_quantity"
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="check_invoice_product_unit_price"
        ),
        CheckConstraint(
            "subtotal >= 0",
            name="check_invoice_product_subtotal"
        ),
    )

    product = relationship(
        "Product",
        back_populates="invoice_products"
    )

    invoice = relationship(
        "Invoice",
        back_populates="invoice_products"
    )

    return_products = relationship(
        "ReturnProduct",
        back_populates="invoice_product"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "subtotal": float(self.subtotal)
        }