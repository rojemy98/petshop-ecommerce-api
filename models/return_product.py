from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SCHEMA_NAME


class ReturnProduct(Base):
    __tablename__ = "return_products"

    id: Mapped[int] = mapped_column(primary_key=True)

    return_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.returns.id"),
        nullable=False
    )

    invoice_product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.invoice_products.id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="check_return_product_quantity"
        ),
    )

    return_request = relationship(
        "Return",
        back_populates="return_products"
    )

    invoice_product = relationship(
        "InvoiceProduct",
        back_populates="return_products"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "invoice_product_id": self.invoice_product_id,
            "quantity": self.quantity
        }