from unittest.mock import Mock

import pytest

from services.invoice_service import InvoiceService


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_session():
    return Mock()


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def invoice_service(
    mock_session,
    mock_repository
):
    service = InvoiceService(
        mock_session
    )

    service.repository = mock_repository

    return service


# ============================================================
# GET INVOICES
# ============================================================

def test_get_invoices_admin(
    invoice_service,
    mock_repository
):
    invoices = [
        Mock(),
        Mock()
    ]

    mock_repository.get_all_with_details.return_value = (
        invoices
    )

    result = invoice_service.get_invoices(
        user_id=10,
        role="ADMIN"
    )

    assert result == invoices

    mock_repository.get_all_with_details.assert_called_once_with()

    mock_repository.get_by_user_id.assert_not_called()


def test_get_invoices_user(
    invoice_service,
    mock_repository
):
    invoices = [
        Mock(),
        Mock()
    ]

    mock_repository.get_by_user_id.return_value = (
        invoices
    )

    result = invoice_service.get_invoices(
        user_id=10,
        role="USER"
    )

    assert result == invoices

    mock_repository.get_by_user_id.assert_called_once_with(
        10
    )

    mock_repository.get_all_with_details.assert_not_called()


# ============================================================
# GET INVOICE BY NUMBER
# ============================================================

def test_get_invoice_by_number_admin(
    invoice_service,
    mock_repository
):
    invoice = Mock()
    invoice.user_id = 20

    mock_repository.get_by_invoice_number.return_value = (
        invoice
    )

    result = invoice_service.get_invoice_by_number(
        invoice_number="INV-123",
        user_id=10,
        role="ADMIN"
    )

    assert result == invoice

    mock_repository.get_by_invoice_number.assert_called_once_with(
        "INV-123"
    )


def test_get_invoice_by_number_user_owner(
    invoice_service,
    mock_repository
):
    invoice = Mock()
    invoice.user_id = 10

    mock_repository.get_by_invoice_number.return_value = (
        invoice
    )

    result = invoice_service.get_invoice_by_number(
        invoice_number="INV-123",
        user_id=10,
        role="USER"
    )

    assert result == invoice

    mock_repository.get_by_invoice_number.assert_called_once_with(
        "INV-123"
    )


def test_get_invoice_by_number_not_found(
    invoice_service,
    mock_repository
):
    mock_repository.get_by_invoice_number.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Invoice not found."
    ):
        invoice_service.get_invoice_by_number(
            invoice_number="INV-999",
            user_id=10,
            role="USER"
        )


def test_get_invoice_by_number_wrong_user(
    invoice_service,
    mock_repository
):
    invoice = Mock()
    invoice.user_id = 20

    mock_repository.get_by_invoice_number.return_value = (
        invoice
    )

    with pytest.raises(
        PermissionError,
        match=(
            "You do not have access "
            "to this invoice."
        )
    ):
        invoice_service.get_invoice_by_number(
            invoice_number="INV-123",
            user_id=10,
            role="USER"
        )