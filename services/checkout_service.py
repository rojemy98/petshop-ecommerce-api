from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from models import (
    Invoice,
    InvoiceProduct,
    Payment,
)

from repositories import (
    CartsRepository,
    ProductsRepository,
    BillingAddressesRepository,
    InvoicesRepository,
    InvoiceProductsRepository,
    PaymentsRepository,
)


class CheckoutService:

    def __init__(self, session: Session, cache_manager):
        self.session = session
        self.cache_manager = cache_manager

        self.carts_repository = CartsRepository(session)
        self.products_repository = ProductsRepository(session)

        self.billing_addresses_repository = (
            BillingAddressesRepository(session)
        )

        self.invoices_repository = InvoicesRepository(
            session
        )

        self.invoice_products_repository = (
            InvoiceProductsRepository(session)
        )

        self.payments_repository = PaymentsRepository(
            session
        )

    def checkout(
        self,
        cart_id: int,
        user_id: int,
        billing_address_id: int,
        payment_method: str,
        payment_reference: str
    ) -> Invoice:

        try:
            cart = (
                self.carts_repository
                .get_cart_with_products(cart_id)
            )

            if cart is None:
                raise LookupError(
                    "Cart not found."
                )

            if cart.user_id != user_id:
                raise PermissionError(
                    "You do not have access to this cart."
                )

            if cart.status != "ACTIVE":
                raise ValueError(
                    "Only active carts can be checked out."
                )

            if not cart.cart_products:
                raise ValueError(
                    "Cannot checkout an empty cart."
                )

            billing_address = (
                self.billing_addresses_repository
                .get_by_id(billing_address_id)
            )

            if billing_address is None:
                raise LookupError(
                    "Billing address not found."
                )

            if billing_address.user_id != user_id:
                raise PermissionError(
                    "You do not have access to this "
                    "billing address."
                )

            total = Decimal("0.00")

            validated_items = []

            product_ids = []

            for cart_item in cart.cart_products:

                product = (
                    self.products_repository
                    .get_by_id(cart_item.product_id)
                )

                if product is None:
                    raise LookupError(
                        f"Product {cart_item.product_id} "
                        f"not found."
                    )

                if not product.is_active:
                    raise ValueError(
                        f"Product '{product.name}' "
                        f"is not available."
                    )

                if product.stock < cart_item.quantity:
                    raise ValueError(
                        f"Insufficient stock for "
                        f"'{product.name}'."
                    )

                unit_price = Decimal(
                    str(product.price)
                )

                subtotal = (
                    unit_price
                    * cart_item.quantity
                )

                total += subtotal

                validated_items.append({
                    "cart_item": cart_item,
                    "product": product,
                    "unit_price": unit_price,
                    "subtotal": subtotal
                })

                product_ids.append(product.id)

            invoice = Invoice(
                user_id=user_id,
                invoice_number=self._generate_invoice_number(),
                billing_address_id=billing_address.id,
                total=total,
                status="PAID"
            )

            self.invoices_repository.create(invoice)

            self.session.flush()

            for item in validated_items:

                invoice_product = InvoiceProduct(
                    product_id=item["product"].id,
                    invoice_id=invoice.id,
                    quantity=item["cart_item"].quantity,
                    unit_price=item["unit_price"],
                    subtotal=item["subtotal"]
                )

                self.invoice_products_repository.create(
                    invoice_product
                )

                item["product"].stock -= (
                    item["cart_item"].quantity
                )

            payment = Payment(
                invoice_id=invoice.id,
                payment_method=payment_method,
                payment_reference=payment_reference,
                status="COMPLETED"
            )

            self.payments_repository.create(payment)

            cart.status = "COMPLETED"

            self.session.commit()

            for product_id in product_ids:
                self.cache_manager.delete_data(
                    f"product:{product_id}"
                )

            self.cache_manager.delete_data(
                "products:all"
            )

            return invoice

        except Exception:
            self.session.rollback()
            raise

    @staticmethod
    def _generate_invoice_number() -> str:
        return f"INV-{uuid4().hex[:12].upper()}"