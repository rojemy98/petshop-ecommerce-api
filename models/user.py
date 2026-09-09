from datetime import datetime, UTC

from sqlalchemy import String, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SCHEMA_NAME


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="CLIENT"
    )

    registration_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('ADMIN', 'CLIENT')",
            name="check_user_role"
        ),
    )

    # Relationships

    login_history = relationship(
        "LoginHistory",
        back_populates="user"
    )

    billing_addresses = relationship(
        "BillingAddress",
        back_populates="user"
    )

    carts = relationship(
        "Cart",
        back_populates="user"
    )

    invoices = relationship(
        "Invoice",
        back_populates="user"
    )

    created_products = relationship(
        "Product",
        foreign_keys="Product.created_by",
        back_populates="creator"
    )

    updated_products = relationship(
        "Product",
        foreign_keys="Product.updated_by",
        back_populates="updater"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "email": self.email,
            "role": self.role,
            "registration_date":
                self.registration_date.isoformat()
                if self.registration_date
                else None
        }