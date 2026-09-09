from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Integer,
    String
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SCHEMA_NAME


class BillingAddress(Base):
    __tablename__ = "billing_addresses"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.users.id"),
        nullable=False
    )

    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    province: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    postal_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="billing_addresses"
    )

    invoices = relationship(
        "Invoice",
        back_populates="billing_address"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "address": self.address,
            "city": self.city,
            "province": self.province,
            "postal_code": self.postal_code,
            "country": self.country
        }