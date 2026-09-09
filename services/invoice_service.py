from sqlalchemy.orm import Session

from models import Invoice
from repositories import InvoicesRepository


class InvoiceService:

    def __init__(self, session: Session):
        self.repository = InvoicesRepository(
            session
        )

    def get_invoices(
        self,
        user_id: int,
        role: str
    ) -> list[Invoice]:

        if role == "ADMIN":
            return (
                self.repository
                .get_all_with_details()
            )

        return self.repository.get_by_user_id(
            user_id
        )

    def get_invoice_by_number(
        self,
        invoice_number: str,
        user_id: int,
        role: str
    ) -> Invoice:

        invoice = (
            self.repository
            .get_by_invoice_number(
                invoice_number
            )
        )

        if invoice is None:
            raise LookupError(
                "Invoice not found."
            )

        if (
            role != "ADMIN"
            and invoice.user_id != user_id
        ):
            raise PermissionError(
                "You do not have access "
                "to this invoice."
            )

        return invoice