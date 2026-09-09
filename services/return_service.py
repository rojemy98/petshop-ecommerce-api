from sqlalchemy.orm import Session

from models import Return, ReturnProduct
from repositories import (
    ReturnsRepository,
    ReturnProductsRepository,
    InvoicesRepository
)


class ReturnService:

    def __init__(self, session: Session, cache_manager):
        self.session = session
        self.cache_manager = cache_manager

        self.returns_repository = (
            ReturnsRepository(session)
        )

        self.return_products_repository = (
            ReturnProductsRepository(session)
        )

        self.invoices_repository = (
            InvoicesRepository(session)
        )

    def get_returns(self, user_id, role):

        if role == "ADMIN":
            return (
                self.returns_repository
                .get_all_with_products()
            )

        return (
            self.returns_repository
            .get_by_user_id(user_id)
        )

    def get_return_by_id(
        self,
        return_id,
        user_id,
        role
    ):

        return_request = (
            self.returns_repository
            .get_by_id(return_id)
        )

        if return_request is None:
            raise LookupError(
                "Return not found."
            )

        if (
            role != "ADMIN"
            and return_request.invoice.user_id
            != user_id
        ):
            raise PermissionError(
                "You do not have access "
                "to this return."
            )

        return return_request

    def create_return(
        self,
        invoice_number: str,
        user_id: int,
        reason: str,
        products: list[dict]
    ) -> Return:

        invoice = (
            self.invoices_repository
            .get_by_invoice_number(
                invoice_number
            )
        )

        if invoice is None:
            raise LookupError(
                "Invoice not found."
            )

        if invoice.user_id != user_id:
            raise PermissionError(
                "You do not have access "
                "to this invoice."
            )

        if invoice.status not in {
            "PAID",
            "PARTIALLY_REFUNDED"
        }:
            raise ValueError(
                "This invoice cannot be returned."
            )

        if not reason or not reason.strip():
            raise ValueError(
                "Return reason is required."
            )

        if not products:
            raise ValueError(
                "At least one product is required."
            )

        validated_products = []

        invoice_product_ids = [
            invoice_product.id
            for invoice_product
            in invoice.invoice_products
        ]

        completed_quantities = (
            self.return_products_repository
            .get_completed_quantities(
                invoice_product_ids
            )
        )

        for item in products:

            invoice_product_id = item.get(
                "invoice_product_id"
            )

            quantity = item.get(
                "quantity"
            )

            self._validate_quantity(quantity)

            invoice_product = next(
                (
                    product
                    for product
                    in invoice.invoice_products
                    if product.id
                    == invoice_product_id
                ),
                None
            )

            if invoice_product is None:
                raise ValueError(
                    f"Invoice product "
                    f"{invoice_product_id} "
                    f"does not belong "
                    f"to this invoice."
                )

            already_returned = (
                completed_quantities.get(
                    invoice_product.id,
                    0
                )
            )

            available_quantity = (
                invoice_product.quantity
                - already_returned
            )

            if quantity > available_quantity:
                raise ValueError(
                    f"Cannot return {quantity} units "
                    f"of invoice product "
                    f"{invoice_product.id}. "
                    f"Only {available_quantity} "
                    f"can still be returned."
                )

            validated_products.append({
                "invoice_product": invoice_product,
                "quantity": quantity
            })

        try:

            return_request = Return(
                invoice_id=invoice.id,
                reason=reason.strip(),
                status="REQUESTED"
            )

            self.returns_repository.create(
                return_request
            )

            self.session.flush()

            for item in validated_products:

                return_product = ReturnProduct(
                    return_id=return_request.id,
                    invoice_product_id=(
                        item["invoice_product"].id
                    ),
                    quantity=item["quantity"]
                )

                self.return_products_repository.create(
                    return_product
                )

            self.session.commit()

            return (
                self.returns_repository
                .get_with_products(
                    return_request.id
                )
            )

        except Exception:
            self.session.rollback()
            raise

    def update_return_status(
        self,
        return_id: int,
        new_status: str
    ) -> Return:

        return_request = (
            self.returns_repository
            .get_with_products(
                return_id
            )
        )

        if return_request is None:
            raise LookupError(
                "Return request not found."
            )

        new_status = new_status.upper()

        allowed_transitions = {
            "REQUESTED": {
                "APPROVED",
                "REJECTED"
            },
            "APPROVED": {
                "COMPLETED"
            },
            "REJECTED": set(),
            "COMPLETED": set()
        }

        allowed_statuses = (
            allowed_transitions.get(
                return_request.status,
                set()
            )
        )

        if new_status not in allowed_statuses:
            raise ValueError(
                f"Cannot change return status "
                f"from {return_request.status} "
                f"to {new_status}."
            )

        try:

            product_ids = []

            if new_status == "COMPLETED":

                return_request.status = (
                    "COMPLETED"
                )

                self.session.flush()

                product_ids = (
                    self._complete_return(
                        return_request
                    )
                )

            else:
                return_request.status = new_status

            self.session.commit()

            for product_id in product_ids:
                self.cache_manager.delete_data(
                    f"product:{product_id}"
                )

            if product_ids:
                self.cache_manager.delete_data(
                    "products:all"
                )

            return (
                self.returns_repository
                .get_with_products(
                    return_id
                )
            )

        except Exception:
            self.session.rollback()
            raise

    def _calculate_invoice_status(
        self,
        invoice
    ) -> str:

        invoice_product_ids = [
            invoice_product.id
            for invoice_product
            in invoice.invoice_products
        ]

        completed_quantities = (
            self.return_products_repository
            .get_completed_quantities(
                invoice_product_ids
            )
        )

        for invoice_product in (
            invoice.invoice_products
        ):

            returned_quantity = (
                completed_quantities.get(
                    invoice_product.id,
                    0
                )
            )

            if (
                returned_quantity
                < invoice_product.quantity
            ):
                return "PARTIALLY_REFUNDED"

        return "REFUNDED"

    @staticmethod
    def _validate_quantity(
        quantity: int
    ) -> None:

        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
        ):
            raise ValueError(
                "Quantity must be an integer."
            )

        if quantity <= 0:
            raise ValueError(
                "Quantity must be "
                "greater than zero."
            )

    def _complete_return(
        self,
        return_request: Return
    ) -> list[int]:

        product_ids = []

        invoice = (
            self.invoices_repository
            .get_by_id_with_details(
                return_request.invoice_id
            )
        )

        if invoice is None:
            raise LookupError(
                "Invoice not found."
            )

        invoice_product_ids = [
            return_product.invoice_product_id
            for return_product
            in return_request.return_products
        ]

        completed_quantities = (
            self.return_products_repository
            .get_completed_quantities(
                invoice_product_ids
            )
        )

        for return_product in (
            return_request.return_products
        ):

            invoice_product = (
                return_product.invoice_product
            )

            if invoice_product is None:
                raise LookupError(
                    "Invoice product not found."
                )

            completed_quantity = (
                completed_quantities.get(
                    invoice_product.id,
                    0
                )
            )

            previously_returned = (
                completed_quantity
                - return_product.quantity
            )

            remaining = (
                invoice_product.quantity
                - previously_returned
            )

            if (
                return_product.quantity
                > remaining
            ):
                raise ValueError(
                    f"Cannot complete return "
                    f"for invoice product "
                    f"{invoice_product.id}. "
                    f"Only {remaining} units "
                    f"remain returnable."
                )

            product = invoice_product.product

            if product is None:
                raise LookupError(
                    "Product not found."
                )

            product.stock += (
                return_product.quantity
            )

            product_ids.append(
                product.id
            )

        self.session.flush()

        invoice.status = (
            self._calculate_invoice_status(
                invoice
            )
        )

        return product_ids