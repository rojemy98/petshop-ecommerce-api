from unittest.mock import Mock

import pytest

from services.return_service import ReturnService


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_session():
    return Mock()


@pytest.fixture
def mock_cache_manager():
    return Mock()


@pytest.fixture
def mock_returns_repository():
    return Mock()


@pytest.fixture
def mock_return_products_repository():
    return Mock()


@pytest.fixture
def mock_invoices_repository():
    return Mock()


@pytest.fixture
def return_service(
    mock_session,
    mock_cache_manager,
    mock_returns_repository,
    mock_return_products_repository,
    mock_invoices_repository
):
    service = ReturnService(
        mock_session,
        mock_cache_manager
    )

    service.returns_repository = (
        mock_returns_repository
    )

    service.return_products_repository = (
        mock_return_products_repository
    )

    service.invoices_repository = (
        mock_invoices_repository
    )

    return service


# ============================================================
# Helper Functions
# ============================================================

def create_product(
    product_id=5,
    stock=10
):
    product = Mock()

    product.id = product_id
    product.stock = stock

    return product


def create_invoice_product(
    invoice_product_id=20,
    product_id=5,
    quantity=5,
    stock=10
):
    product = create_product(
        product_id=product_id,
        stock=stock
    )

    invoice_product = Mock()

    invoice_product.id = invoice_product_id
    invoice_product.product_id = product_id
    invoice_product.quantity = quantity
    invoice_product.product = product

    return invoice_product


def create_invoice(
    invoice_id=100,
    user_id=10,
    status="PAID",
    invoice_products=None
):
    invoice = Mock()

    invoice.id = invoice_id
    invoice.user_id = user_id
    invoice.status = status

    if invoice_products is None:
        invoice_products = [
            create_invoice_product()
        ]

    invoice.invoice_products = invoice_products

    return invoice


def create_return_product(
    invoice_product=None,
    quantity=2
):
    if invoice_product is None:
        invoice_product = create_invoice_product()

    return_product = Mock()

    return_product.invoice_product = (
        invoice_product
    )

    return_product.invoice_product_id = (
        invoice_product.id
    )

    return_product.quantity = quantity

    return return_product


def create_return_request(
    return_id=1,
    invoice_id=100,
    status="REQUESTED",
    return_products=None
):
    return_request = Mock()

    return_request.id = return_id
    return_request.invoice_id = invoice_id
    return_request.status = status

    if return_products is None:
        return_products = []

    return_request.return_products = (
        return_products
    )

    return return_request


# ============================================================
# CREATE RETURN - SUCCESS
# ============================================================

def test_create_return_success(
    return_service,
    mock_session,
    mock_returns_repository,
    mock_return_products_repository,
    mock_invoices_repository
):
    invoice_product = create_invoice_product(
        invoice_product_id=20,
        quantity=5
    )

    invoice = create_invoice(
        invoice_id=100,
        user_id=10,
        status="PAID",
        invoice_products=[
            invoice_product
        ]
    )

    mock_invoices_repository.get_by_invoice_number.return_value = (
        invoice
    )

    mock_returns_repository.get_completed_quantity.return_value = (
        1
    )

    def assign_return_id(return_request):
        return_request.id = 50
        return return_request

    mock_returns_repository.create.side_effect = (
        assign_return_id
    )

    saved_return = Mock()
    saved_return.id = 50

    mock_returns_repository.get_with_products.return_value = (
        saved_return
    )

    result = return_service.create_return(
        invoice_number="INV-123",
        user_id=10,
        reason="Product damaged",
        products=[
            {
                "invoice_product_id": 20,
                "quantity": 2
            }
        ]
    )

    assert result == saved_return

    mock_invoices_repository.get_by_invoice_number.assert_called_once_with(
        "INV-123"
    )

    mock_returns_repository.get_completed_quantity.assert_called_once_with(
        20
    )

    mock_returns_repository.create.assert_called_once()

    created_return = (
        mock_returns_repository
        .create
        .call_args[0][0]
    )

    assert created_return.invoice_id == 100
    assert created_return.reason == "Product damaged"
    assert created_return.status == "REQUESTED"

    mock_return_products_repository.create.assert_called_once()

    return_product = (
        mock_return_products_repository
        .create
        .call_args[0][0]
    )

    assert return_product.return_id == 50
    assert return_product.invoice_product_id == 20
    assert return_product.quantity == 2

    mock_session.flush.assert_called_once_with()
    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_create_return_strips_reason(
    return_service,
    mock_returns_repository,
    mock_return_products_repository,
    mock_invoices_repository
):
    invoice_product = create_invoice_product()

    invoice = create_invoice(
        invoice_products=[
            invoice_product
        ]
    )

    mock_invoices_repository.get_by_invoice_number.return_value = (
        invoice
    )

    mock_returns_repository.get_completed_quantity.return_value = (
        0
    )

    def assign_return_id(return_request):
        return_request.id = 50

    mock_returns_repository.create.side_effect = (
        assign_return_id
    )

    mock_returns_repository.get_with_products.return_value = (
        Mock()
    )

    return_service.create_return(
        invoice_number="INV-123",
        user_id=10,
        reason="   Damaged item   ",
        products=[
            {
                "invoice_product_id": 20,
                "quantity": 1
            }
        ]
    )

    created_return = (
        mock_returns_repository
        .create
        .call_args[0][0]
    )

    assert created_return.reason == "Damaged item"


# ============================================================
# CREATE RETURN - INVOICE VALIDATION
# ============================================================

def test_create_return_invoice_not_found(
    return_service,
    mock_invoices_repository
):
    mock_invoices_repository.get_by_invoice_number.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Invoice not found."
    ):
        return_service.create_return(
            invoice_number="INV-999",
            user_id=10,
            reason="Damaged",
            products=[
                {
                    "invoice_product_id": 20,
                    "quantity": 1
                }
            ]
        )


def test_create_return_wrong_user(
    return_service,
    mock_invoices_repository
):
    invoice = create_invoice(
        user_id=20
    )

    mock_invoices_repository.get_by_invoice_number.return_value = (
        invoice
    )

    with pytest.raises(
        PermissionError,
        match="You do not have access to this invoice."
    ):
        return_service.create_return(
            invoice_number="INV-123",
            user_id=10,
            reason="Damaged",
            products=[
                {
                    "invoice_product_id": 20,
                    "quantity": 1
                }
            ]
        )


def test_create_return_invalid_invoice_status(
    return_service,
    mock_invoices_repository
):
    invoice = create_invoice(
        status="REFUNDED"
    )

    mock_invoices_repository.get_by_invoice_number.return_value = (
        invoice
    )

    with pytest.raises(
        ValueError,
        match="This invoice cannot be returned."
    ):
        return_service.create_return(
            invoice_number="INV-123",
            user_id=10,
            reason="Damaged",
            products=[
                {
                    "invoice_product_id": 20,
                    "quantity": 1
                }
            ]
        )


def test_create_return_allows_partially_refunded_invoice(
    return_service,
    mock_returns_repository,
    mock_invoices_repository
):
    invoice_product = create_invoice_product()

    invoice = create_invoice(
        status="PARTIALLY_REFUNDED",
        invoice_products=[
            invoice_product
        ]
    )

    mock_invoices_repository.get_by_invoice_number.return_value = (
        invoice
    )

    mock_returns_repository.get_completed_quantity.return_value = (
        0
    )

    def assign_return_id(return_request):
        return_request.id = 50

    mock_returns_repository.create.side_effect = (
        assign_return_id
    )

    mock_returns_repository.get_with_products.return_value = (
        Mock()
    )

    result = return_service.create_return(
        invoice_number="INV-123",
        user_id=10,
        reason="Damaged",
        products=[
            {
                "invoice_product_id": 20,
                "quantity": 1
            }
        ]
    )

    assert result is not None


# ============================================================
# CREATE RETURN - INPUT VALIDATION
# ============================================================

def test_create_return_empty_reason(
    return_service,
    mock_invoices_repository
):
    invoice = create_invoice()

    mock_invoices_repository.get_by_invoice_number.return_value = (
        invoice
    )

    with pytest.raises(
        ValueError,
        match="Return reason is required."
    ):
        return_service.create_return(
            invoice_number="INV-123",
            user_id=10,
            reason="   ",
            products=[
                {
                    "invoice_product_id": 20,
                    "quantity": 1
                }
            ]
        )


def test_create_return_empty_products(
    return_service,
    mock_invoices_repository
):
    invoice = create_invoice()

    mock_invoices_repository.get_by_invoice_number.return_value = (
        invoice
    )

    with pytest.raises(
        ValueError,
        match="At least one product is required."
    ):
        return_service.create_return(
            invoice_number="INV-123",
            user_id=10,
            reason="Damaged",
            products=[]
        )


def test_create_return_invoice_product_not_in_invoice(
    return_service,
    mock_invoices_repository
):
    invoice_product = create_invoice_product(
        invoice_product_id=20
    )

    invoice = create_invoice(
        invoice_products=[
            invoice_product
        ]
    )

    mock_invoices_repository.get_by_invoice_number.return_value = (
        invoice
    )

    with pytest.raises(
        ValueError,
        match=(
            "Invoice product 999 "
            "does not belong to this invoice."
        )
    ):
        return_service.create_return(
            invoice_number="INV-123",
            user_id=10,
            reason="Damaged",
            products=[
                {
                    "invoice_product_id": 999,
                    "quantity": 1
                }
            ]
        )


def test_create_return_quantity_exceeds_available(
    return_service,
    mock_returns_repository,
    mock_invoices_repository
):
    invoice_product = create_invoice_product(
        invoice_product_id=20,
        quantity=5
    )

    invoice = create_invoice(
        invoice_products=[
            invoice_product
        ]
    )

    mock_invoices_repository.get_by_invoice_number.return_value = (
        invoice
    )

    mock_returns_repository.get_completed_quantity.return_value = (
        3
    )

    with pytest.raises(
        ValueError,
        match=(
            "Cannot return 3 units "
            "of invoice product 20."
        )
    ):
        return_service.create_return(
            invoice_number="INV-123",
            user_id=10,
            reason="Damaged",
            products=[
                {
                    "invoice_product_id": 20,
                    "quantity": 3
                }
            ]
        )


# ============================================================
# CREATE RETURN - TRANSACTION
# ============================================================

def test_create_return_rolls_back_on_repository_error(
    return_service,
    mock_session,
    mock_returns_repository,
    mock_invoices_repository
):
    invoice_product = create_invoice_product()

    invoice = create_invoice(
        invoice_products=[
            invoice_product
        ]
    )

    mock_invoices_repository.get_by_invoice_number.return_value = (
        invoice
    )

    mock_returns_repository.get_completed_quantity.return_value = (
        0
    )

    mock_returns_repository.create.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        return_service.create_return(
            invoice_number="INV-123",
            user_id=10,
            reason="Damaged",
            products=[
                {
                    "invoice_product_id": 20,
                    "quantity": 1
                }
            ]
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


# ============================================================
# UPDATE RETURN STATUS
# ============================================================

def test_update_return_status_requested_to_approved(
    return_service,
    mock_returns_repository,
    mock_session
):
    return_request = create_return_request(
        return_id=1,
        status="REQUESTED"
    )

    updated_return = Mock()

    mock_returns_repository.get_with_products.side_effect = [
        return_request,
        updated_return
    ]

    result = return_service.update_return_status(
        return_id=1,
        new_status="approved"
    )

    assert result == updated_return
    assert return_request.status == "APPROVED"

    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_update_return_status_requested_to_rejected(
    return_service,
    mock_returns_repository,
    mock_session
):
    return_request = create_return_request(
        status="REQUESTED"
    )

    mock_returns_repository.get_with_products.side_effect = [
        return_request,
        return_request
    ]

    result = return_service.update_return_status(
        return_id=1,
        new_status="REJECTED"
    )

    assert result.status == "REJECTED"

    mock_session.commit.assert_called_once_with()


def test_update_return_status_not_found(
    return_service,
    mock_returns_repository
):
    mock_returns_repository.get_with_products.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Return request not found."
    ):
        return_service.update_return_status(
            return_id=999,
            new_status="APPROVED"
        )


def test_update_return_status_invalid_transition(
    return_service,
    mock_returns_repository,
    mock_session
):
    return_request = create_return_request(
        status="REQUESTED"
    )

    mock_returns_repository.get_with_products.return_value = (
        return_request
    )

    with pytest.raises(
        ValueError,
        match=(
            "Cannot change return status "
            "from REQUESTED to COMPLETED."
        )
    ):
        return_service.update_return_status(
            return_id=1,
            new_status="COMPLETED"
        )

    mock_session.commit.assert_not_called()


def test_update_return_status_completed_is_terminal(
    return_service,
    mock_returns_repository
):
    return_request = create_return_request(
        status="COMPLETED"
    )

    mock_returns_repository.get_with_products.return_value = (
        return_request
    )

    with pytest.raises(
        ValueError,
        match=(
            "Cannot change return status "
            "from COMPLETED to APPROVED."
        )
    ):
        return_service.update_return_status(
            return_id=1,
            new_status="APPROVED"
        )


def test_update_return_status_rejected_is_terminal(
    return_service,
    mock_returns_repository
):
    return_request = create_return_request(
        status="REJECTED"
    )

    mock_returns_repository.get_with_products.return_value = (
        return_request
    )

    with pytest.raises(
        ValueError,
        match=(
            "Cannot change return status "
            "from REJECTED to APPROVED."
        )
    ):
        return_service.update_return_status(
            return_id=1,
            new_status="APPROVED"
        )


# ============================================================
# COMPLETE RETURN
# ============================================================

def test_complete_return_restores_stock(
    return_service,
    mock_returns_repository,
    mock_invoices_repository
):
    invoice_product = create_invoice_product(
        invoice_product_id=20,
        product_id=5,
        quantity=5,
        stock=10
    )

    return_product = create_return_product(
        invoice_product=invoice_product,
        quantity=2
    )

    return_request = create_return_request(
        invoice_id=100,
        status="COMPLETED",
        return_products=[
            return_product
        ]
    )

    invoice = create_invoice(
        invoice_id=100,
        invoice_products=[
            invoice_product
        ]
    )

    mock_invoices_repository.get_by_id_with_details.return_value = (
        invoice
    )

    # completed_quantity includes the current return
    mock_returns_repository.get_completed_quantity.return_value = (
        2
    )

    product_ids = return_service._complete_return(
        return_request
    )

    assert invoice_product.product.stock == 12
    assert product_ids == [5]


def test_complete_return_invoice_not_found(
    return_service,
    mock_invoices_repository
):
    return_request = create_return_request(
        invoice_id=999
    )

    mock_invoices_repository.get_by_id_with_details.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Invoice not found."
    ):
        return_service._complete_return(
            return_request
        )


def test_complete_return_invoice_product_not_found(
    return_service,
    mock_invoices_repository
):
    return_product = Mock()

    return_product.invoice_product = None

    return_request = create_return_request(
        return_products=[
            return_product
        ]
    )

    invoice = create_invoice()

    mock_invoices_repository.get_by_id_with_details.return_value = (
        invoice
    )

    with pytest.raises(
        LookupError,
        match="Invoice product not found."
    ):
        return_service._complete_return(
            return_request
        )


def test_complete_return_product_not_found(
    return_service,
    mock_returns_repository,
    mock_invoices_repository
):
    invoice_product = create_invoice_product(
        quantity=5
    )

    invoice_product.product = None

    return_product = create_return_product(
        invoice_product=invoice_product,
        quantity=2
    )

    return_request = create_return_request(
        return_products=[
            return_product
        ]
    )

    invoice = create_invoice(
        invoice_products=[
            invoice_product
        ]
    )

    mock_invoices_repository.get_by_id_with_details.return_value = (
        invoice
    )

    mock_returns_repository.get_completed_quantity.return_value = (
        2
    )

    with pytest.raises(
        LookupError,
        match="Product not found."
    ):
        return_service._complete_return(
            return_request
        )


def test_complete_return_quantity_exceeds_remaining(
    return_service,
    mock_returns_repository,
    mock_invoices_repository
):
    invoice_product = create_invoice_product(
        invoice_product_id=20,
        quantity=5
    )

    return_product = create_return_product(
        invoice_product=invoice_product,
        quantity=3
    )

    return_request = create_return_request(
        return_products=[
            return_product
        ]
    )

    invoice = create_invoice(
        invoice_products=[
            invoice_product
        ]
    )

    mock_invoices_repository.get_by_id_with_details.return_value = (
        invoice
    )

    # 4 completed total, including current 3
    # previously returned = 4 - 3 = 1
    # remaining = 5 - 1 = 4
    # Current return 3 is valid.
    #
    # To make it invalid:
    # completed quantity = 6
    # previously returned = 6 - 3 = 3
    # remaining = 2
    mock_returns_repository.get_completed_quantity.return_value = (
        6
    )

    with pytest.raises(
        ValueError,
        match=(
            "Cannot complete return for "
            "invoice product 20."
        )
    ):
        return_service._complete_return(
            return_request
        )


# ============================================================
# INVOICE STATUS CALCULATION
# ============================================================

def test_calculate_invoice_status_refunded(
    return_service,
    mock_returns_repository
):
    product_1 = create_invoice_product(
        invoice_product_id=20,
        quantity=2
    )

    product_2 = create_invoice_product(
        invoice_product_id=21,
        quantity=3
    )

    invoice = create_invoice(
        invoice_products=[
            product_1,
            product_2
        ]
    )

    mock_returns_repository.get_completed_quantity.side_effect = [
        2,
        3
    ]

    result = (
        return_service._calculate_invoice_status(
            invoice
        )
    )

    assert result == "REFUNDED"


def test_calculate_invoice_status_partially_refunded(
    return_service,
    mock_returns_repository
):
    product_1 = create_invoice_product(
        invoice_product_id=20,
        quantity=2
    )

    product_2 = create_invoice_product(
        invoice_product_id=21,
        quantity=3
    )

    invoice = create_invoice(
        invoice_products=[
            product_1,
            product_2
        ]
    )

    mock_returns_repository.get_completed_quantity.side_effect = [
        2,
        1
    ]

    result = (
        return_service._calculate_invoice_status(
            invoice
        )
    )

    assert result == "PARTIALLY_REFUNDED"


# ============================================================
# COMPLETED STATUS + CACHE
# ============================================================

def test_update_return_status_completed_restores_stock_and_invalidates_cache(
    return_service,
    mock_returns_repository,
    mock_invoices_repository,
    mock_cache_manager,
    mock_session
):
    invoice_product = create_invoice_product(
        invoice_product_id=20,
        product_id=5,
        quantity=5,
        stock=10
    )

    return_product = create_return_product(
        invoice_product=invoice_product,
        quantity=2
    )

    return_request = create_return_request(
        return_id=1,
        invoice_id=100,
        status="APPROVED",
        return_products=[
            return_product
        ]
    )

    invoice = create_invoice(
        invoice_id=100,
        invoice_products=[
            invoice_product
        ]
    )

    updated_return = Mock()

    mock_returns_repository.get_with_products.side_effect = [
        return_request,
        updated_return
    ]

    mock_invoices_repository.get_by_id_with_details.return_value = (
        invoice
    )

    # First call: _complete_return()
    # Second call: _calculate_invoice_status()
    mock_returns_repository.get_completed_quantity.side_effect = [
        2,
        2
    ]

    result = return_service.update_return_status(
        return_id=1,
        new_status="COMPLETED"
    )

    assert result == updated_return

    assert return_request.status == "COMPLETED"

    assert invoice_product.product.stock == 12

    assert invoice.status == (
        "PARTIALLY_REFUNDED"
    )

    assert mock_session.flush.call_count == 2

    mock_session.commit.assert_called_once_with()

    mock_cache_manager.delete_data.assert_any_call(
        "product:5"
    )

    mock_cache_manager.delete_data.assert_any_call(
        "products:all"
    )


def test_approved_status_does_not_modify_stock_or_cache(
    return_service,
    mock_returns_repository,
    mock_cache_manager
):
    return_request = create_return_request(
        status="REQUESTED"
    )

    mock_returns_repository.get_with_products.side_effect = [
        return_request,
        return_request
    ]

    return_service.update_return_status(
        return_id=1,
        new_status="APPROVED"
    )

    assert return_request.status == "APPROVED"

    mock_cache_manager.delete_data.assert_not_called()


# ============================================================
# UPDATE STATUS - TRANSACTION ERROR
# ============================================================

def test_update_return_status_rolls_back_on_commit_error(
    return_service,
    mock_returns_repository,
    mock_session
):
    return_request = create_return_request(
        status="REQUESTED"
    )

    mock_returns_repository.get_with_products.return_value = (
        return_request
    )

    mock_session.commit.side_effect = (
        Exception("Commit error")
    )

    with pytest.raises(
        Exception,
        match="Commit error"
    ):
        return_service.update_return_status(
            return_id=1,
            new_status="APPROVED"
        )

    mock_session.rollback.assert_called_once_with()


# ============================================================
# QUANTITY VALIDATION
# ============================================================

def test_validate_quantity_success():
    ReturnService._validate_quantity(
        3
    )


def test_validate_quantity_zero():
    with pytest.raises(
        ValueError,
        match="Quantity must be greater than zero."
    ):
        ReturnService._validate_quantity(
            0
        )


def test_validate_quantity_negative():
    with pytest.raises(
        ValueError,
        match="Quantity must be greater than zero."
    ):
        ReturnService._validate_quantity(
            -1
        )


def test_validate_quantity_float():
    with pytest.raises(
        ValueError,
        match="Quantity must be an integer."
    ):
        ReturnService._validate_quantity(
            2.5
        )


def test_validate_quantity_string():
    with pytest.raises(
        ValueError,
        match="Quantity must be an integer."
    ):
        ReturnService._validate_quantity(
            "2"
        )


def test_validate_quantity_boolean():
    with pytest.raises(
        ValueError,
        match="Quantity must be an integer."
    ):
        ReturnService._validate_quantity(
            True
        )