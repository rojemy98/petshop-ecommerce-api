from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from models import Product
from repositories import ProductsRepository


class ProductService:

    def __init__(self, session: Session):
        self.session = session
        self.products_repository = ProductsRepository(session)

    def get_all_products(self) -> list[Product]:
        return self.products_repository.get_all()

    def get_available_products(self):
        return (
            self.products_repository.get_available_products()
        )

    def get_product_by_id(
        self,
        product_id: int
    ) -> Product:

        product = self.products_repository.get_by_id(product_id)

        if product is None:
            raise LookupError("Product not found.")

        return product

    def create_product(
        self,
        data: dict,
        user_id: int
    ) -> Product:

        existing_product = self.products_repository.get_by_name(
            data["name"]
        )

        if existing_product:
            raise ValueError(
                "A product with this name already exists."
            )

        price = self._validate_price(data["price"])
        stock = self._validate_stock(data["stock"])

        product = Product(
            name=data["name"].strip(),
            price=price,
            stock=stock,
            created_by=user_id
        )

        try:
            self.products_repository.create(product)
            self.session.commit()

            return product

        except Exception:
            self.session.rollback()
            raise

    def update_product(
        self,
        product_id: int,
        data: dict,
        user_id: int
    ) -> Product:

        product = self.get_product_by_id(product_id)

        allowed_fields = {
            "name",
            "price",
            "stock",
            "is_active"
        }

        invalid_fields = set(data) - allowed_fields

        if invalid_fields:
            raise ValueError(
                f"Fields cannot be updated: "
                f"{', '.join(invalid_fields)}."
            )

        # Validate product name
        if "name" in data:
            name = data["name"].strip()

            if not name:
                raise ValueError(
                    "Product name cannot be empty."
                )

            existing_product = (
                self.products_repository.get_by_name(name)
            )

            if (
                existing_product
                and existing_product.id != product.id
            ):
                raise ValueError(
                    "A product with this name already exists."
                )

            product.name = name

        # Validate price
        if "price" in data:
            product.price = self._validate_price(
                data["price"]
            )

        # Validate stock
        if "stock" in data:
            product.stock = self._validate_stock(
                data["stock"]
            )

        # Validate active status
        if "is_active" in data:

            if not isinstance(data["is_active"], bool):
                raise ValueError(
                    "is_active must be a boolean."
                )

            product.is_active = data["is_active"]

        # Audit field
        product.updated_by = user_id

        try:
            self.products_repository.update(product)
            self.session.commit()

            return product

        except Exception:
            self.session.rollback()
            raise

    def delete_product(
        self,
        product_id: int,
        user_id: int
    ) -> None:

        product = self.get_product_by_id(product_id)

        product.is_active = False
        product.updated_by = user_id

        try:
            self.products_repository.update(product)
            self.session.commit()

        except Exception:
            self.session.rollback()
            raise

    @staticmethod
    def _validate_price(value) -> Decimal:
        try:
            price = Decimal(str(value))

        except (InvalidOperation, TypeError, ValueError):
            raise ValueError(
                "Price must be a valid number."
            )

        if price < 0:
            raise ValueError(
                "Price cannot be negative."
            )

        return price

    @staticmethod
    def _validate_stock(value) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(
                "Stock must be an integer."
            )

        if value < 0:
            raise ValueError(
                "Stock cannot be negative."
            )

        return value