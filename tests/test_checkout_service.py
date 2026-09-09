from decimal import Decimal
from unittest.mock import Mock

import pytest

from services.checkout_service import CheckoutService


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
def mock_carts_repository():
    return Mock()


@pytest.fixture
def mock_products_repository():
    return Mock()


@pytest.fixture
def mock_billing_addresses_repository():
    return Mock()


@pytest.fixture
def mock_invoices_repository():
    return Mock()


@pytest.fixture
def mock_invoice_products_repository():
    return Mock()


@pytest.fixture
def mock_payments_repository():
    return Mock()


@pytest.fixture
def checkout_service(
    mock_session,
    mock_cache_manager,
    mock_carts_repository,
    mock_products_repository,
    mock_billing_addresses_repository,
    mock_invoices_repository,
    mock_invoice_products_repository,
    mock_payments_repository
):
    service = CheckoutService(
        mock_session,
        mock_cache_manager
    )

    service.carts_repository = (
        mock_carts_repository
    )

    service.products_repository = (
        mock_products_repository
    )

    service.billing_addresses_repository = (
        mock_billing_addresses_repository
    )

    service.invoices_repository = (
        mock_invoices_repository
    )

    service.invoice_products_repository = (
        mock_invoice_products_repository
    )

    service.payments_repository = (
        mock_payments_repository
    )

    return service


# ============================================================
# Helper Functions
# ============================================================

def create_cart_item(
    product_id=5,
    quantity=2
):
    cart_item = Mock()

    cart_item.product_id = product_id
    cart_item.quantity = quantity

    return cart_item


def create_product(
    product_id=5,
    name="Dog Food",
    price="10.50",
    stock=20,
    is_active=True
):
    product = Mock()

    product.id = product_id
    product.name = name
    product.price = Decimal(price)
    product.stock = stock
    product.is_active = is_active

    return product


def create_active_cart(
    cart_id=1,
    user_id=10,
    cart_products=None
):
    cart = Mock()

    cart.id = cart_id
    cart.user_id = user_id
    cart.status = "ACTIVE"

    if cart_products is None:
        cart_products = [
            create_cart_item()
        ]

    cart.cart_products = cart_products

    return cart


def create_billing_address(
    address_id=3,
    user_id=10
):
    billing_address = Mock()

    billing_address.id = address_id
    billing_address.user_id = user_id

    return billing_address


# ============================================================
# SUCCESSFUL CHECKOUT
# ============================================================

def test_checkout_success(
    checkout_service,
    mock_session,
    mock_cache_manager,
    mock_carts_repository,
    mock_products_repository,
    mock_billing_addresses_repository,
    mock_invoices_repository,
    mock_invoice_products_repository,
    mock_payments_repository
):
    cart_item = create_cart_item(
        product_id=5,
        quantity=2
    )

    cart = create_active_cart(
        cart_products=[cart_item]
    )

    product = create_product(
        product_id=5,
        price="10.50",
        stock=20
    )

    billing_address = create_billing_address()

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    mock_billing_addresses_repository.get_by_id.return_value = (
        billing_address
    )

    # Simulates PostgreSQL assigning an ID
    # after the Invoice is inserted/flushed.
    def assign_invoice_id(invoice):
        invoice.id = 100
        return invoice

    mock_invoices_repository.create.side_effect = (
        assign_invoice_id
    )

    result = checkout_service.checkout(
        cart_id=1,
        user_id=10,
        billing_address_id=3,
        payment_method="SINPE",
        payment_reference="SINPE-001"
    )

    # --------------------------------------------------------
    # Invoice
    # --------------------------------------------------------

    assert result.user_id == 10
    assert result.billing_address_id == 3
    assert result.total == Decimal("21.00")
    assert result.status == "PAID"

    assert result.invoice_number.startswith(
        "INV-"
    )

    # --------------------------------------------------------
    # Invoice creation
    # --------------------------------------------------------

    mock_invoices_repository.create.assert_called_once()

    created_invoice = (
        mock_invoices_repository
        .create
        .call_args[0][0]
    )

    assert created_invoice == result

    # --------------------------------------------------------
    # InvoiceProduct
    # --------------------------------------------------------

    mock_invoice_products_repository.create.assert_called_once()

    invoice_product = (
        mock_invoice_products_repository
        .create
        .call_args[0][0]
    )

    assert invoice_product.product_id == 5
    assert invoice_product.invoice_id == 100
    assert invoice_product.quantity == 2

    assert invoice_product.unit_price == Decimal(
        "10.50"
    )

    assert invoice_product.subtotal == Decimal(
        "21.00"
    )

    # --------------------------------------------------------
    # Stock
    # --------------------------------------------------------

    assert product.stock == 18

    # --------------------------------------------------------
    # Payment
    # --------------------------------------------------------

    mock_payments_repository.create.assert_called_once()

    payment = (
        mock_payments_repository
        .create
        .call_args[0][0]
    )

    assert payment.invoice_id == 100
    assert payment.payment_method == "SINPE"

    assert (
        payment.payment_reference
        == "SINPE-001"
    )

    assert payment.status == "COMPLETED"

    # --------------------------------------------------------
    # Cart
    # --------------------------------------------------------

    assert cart.status == "COMPLETED"

    # --------------------------------------------------------
    # Transaction
    # --------------------------------------------------------

    mock_session.flush.assert_called_once_with()
    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()

    # --------------------------------------------------------
    # Cache invalidation
    # --------------------------------------------------------

    mock_cache_manager.delete_data.assert_any_call(
        "product:5"
    )

    mock_cache_manager.delete_data.assert_any_call(
        "products:all"
    )


# ============================================================
# CHECKOUT WITH MULTIPLE PRODUCTS
# ============================================================

def test_checkout_multiple_products_calculates_total(
    checkout_service,
    mock_carts_repository,
    mock_products_repository,
    mock_billing_addresses_repository,
    mock_invoices_repository,
    mock_invoice_products_repository,
    mock_cache_manager
):
    item_1 = create_cart_item(
        product_id=5,
        quantity=2
    )

    item_2 = create_cart_item(
        product_id=6,
        quantity=3
    )

    cart = create_active_cart(
        cart_products=[
            item_1,
            item_2
        ]
    )

    product_1 = create_product(
        product_id=5,
        name="Dog Food",
        price="10.00",
        stock=20
    )

    product_2 = create_product(
        product_id=6,
        name="Cat Food",
        price="5.50",
        stock=15
    )

    billing_address = create_billing_address()

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.side_effect = [
        product_1,
        product_2
    ]

    mock_billing_addresses_repository.get_by_id.return_value = (
        billing_address
    )

    def assign_invoice_id(invoice):
        invoice.id = 100
        return invoice

    mock_invoices_repository.create.side_effect = (
        assign_invoice_id
    )

    invoice = checkout_service.checkout(
        cart_id=1,
        user_id=10,
        billing_address_id=3,
        payment_method="CARD",
        payment_reference="CARD-001"
    )

    # 10.00 * 2 = 20.00
    # 5.50 * 3 = 16.50
    # Total       = 36.50

    assert invoice.total == Decimal("36.50")

    assert product_1.stock == 18
    assert product_2.stock == 12

    assert (
        mock_invoice_products_repository
        .create
        .call_count
        == 2
    )

    mock_cache_manager.delete_data.assert_any_call(
        "product:5"
    )

    mock_cache_manager.delete_data.assert_any_call(
        "product:6"
    )

    mock_cache_manager.delete_data.assert_any_call(
        "products:all"
    )


# ============================================================
# CART VALIDATION
# ============================================================

def test_checkout_cart_not_found(
    checkout_service,
    mock_carts_repository,
    mock_session
):
    mock_carts_repository.get_cart_with_products.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Cart not found."
    ):
        checkout_service.checkout(
            cart_id=999,
            user_id=10,
            billing_address_id=3,
            payment_method="SINPE",
            payment_reference="SINPE-001"
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


def test_checkout_cart_wrong_user(
    checkout_service,
    mock_carts_repository,
    mock_session
):
    cart = create_active_cart(
        user_id=20
    )

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    with pytest.raises(
        PermissionError,
        match="You do not have access to this cart."
    ):
        checkout_service.checkout(
            cart_id=1,
            user_id=10,
            billing_address_id=3,
            payment_method="SINPE",
            payment_reference="SINPE-001"
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


def test_checkout_non_active_cart(
    checkout_service,
    mock_carts_repository,
    mock_session
):
    cart = create_active_cart()

    cart.status = "COMPLETED"

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    with pytest.raises(
        ValueError,
        match="Only active carts can be checked out."
    ):
        checkout_service.checkout(
            cart_id=1,
            user_id=10,
            billing_address_id=3,
            payment_method="SINPE",
            payment_reference="SINPE-001"
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


def test_checkout_empty_cart(
    checkout_service,
    mock_carts_repository,
    mock_session
):
    cart = create_active_cart(
        cart_products=[]
    )

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    with pytest.raises(
        ValueError,
        match="Cannot checkout an empty cart."
    ):
        checkout_service.checkout(
            cart_id=1,
            user_id=10,
            billing_address_id=3,
            payment_method="SINPE",
            payment_reference="SINPE-001"
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


# ============================================================
# BILLING ADDRESS VALIDATION
# ============================================================

def test_checkout_billing_address_not_found(
    checkout_service,
    mock_carts_repository,
    mock_billing_addresses_repository,
    mock_session
):
    cart = create_active_cart()

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_billing_addresses_repository.get_by_id.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Billing address not found."
    ):
        checkout_service.checkout(
            cart_id=1,
            user_id=10,
            billing_address_id=999,
            payment_method="SINPE",
            payment_reference="SINPE-001"
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


def test_checkout_billing_address_wrong_user(
    checkout_service,
    mock_carts_repository,
    mock_billing_addresses_repository,
    mock_session
):
    cart = create_active_cart()

    billing_address = create_billing_address(
        user_id=20
    )

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_billing_addresses_repository.get_by_id.return_value = (
        billing_address
    )

    with pytest.raises(
        PermissionError,
        match=(
            "You do not have access to this "
            "billing address."
        )
    ):
        checkout_service.checkout(
            cart_id=1,
            user_id=10,
            billing_address_id=3,
            payment_method="SINPE",
            payment_reference="SINPE-001"
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


# ============================================================
# PRODUCT VALIDATION
# ============================================================

def test_checkout_product_not_found(
    checkout_service,
    mock_carts_repository,
    mock_billing_addresses_repository,
    mock_products_repository,
    mock_session
):
    item = create_cart_item(
        product_id=5
    )

    cart = create_active_cart(
        cart_products=[item]
    )

    billing_address = create_billing_address()

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_billing_addresses_repository.get_by_id.return_value = (
        billing_address
    )

    mock_products_repository.get_by_id.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Product 5 not found."
    ):
        checkout_service.checkout(
            cart_id=1,
            user_id=10,
            billing_address_id=3,
            payment_method="SINPE",
            payment_reference="SINPE-001"
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


def test_checkout_inactive_product(
    checkout_service,
    mock_carts_repository,
    mock_billing_addresses_repository,
    mock_products_repository,
    mock_session
):
    item = create_cart_item(
        product_id=5
    )

    cart = create_active_cart(
        cart_products=[item]
    )

    billing_address = create_billing_address()

    product = create_product(
        product_id=5,
        name="Dog Food",
        is_active=False
    )

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_billing_addresses_repository.get_by_id.return_value = (
        billing_address
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    with pytest.raises(
        ValueError,
        match="Product 'Dog Food' is not available."
    ):
        checkout_service.checkout(
            cart_id=1,
            user_id=10,
            billing_address_id=3,
            payment_method="SINPE",
            payment_reference="SINPE-001"
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


def test_checkout_insufficient_stock(
    checkout_service,
    mock_carts_repository,
    mock_billing_addresses_repository,
    mock_products_repository,
    mock_session
):
    item = create_cart_item(
        product_id=5,
        quantity=10
    )

    cart = create_active_cart(
        cart_products=[item]
    )

    billing_address = create_billing_address()

    product = create_product(
        product_id=5,
        name="Dog Food",
        stock=5
    )

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_billing_addresses_repository.get_by_id.return_value = (
        billing_address
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    with pytest.raises(
        ValueError,
        match="Insufficient stock for 'Dog Food'."
    ):
        checkout_service.checkout(
            cart_id=1,
            user_id=10,
            billing_address_id=3,
            payment_method="SINPE",
            payment_reference="SINPE-001"
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


# ============================================================
# DATABASE TRANSACTION
# ============================================================

def test_checkout_rolls_back_if_invoice_creation_fails(
    checkout_service,
    mock_carts_repository,
    mock_products_repository,
    mock_billing_addresses_repository,
    mock_invoices_repository,
    mock_session
):
    cart = create_active_cart()

    product = create_product()

    billing_address = create_billing_address()

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    mock_billing_addresses_repository.get_by_id.return_value = (
        billing_address
    )

    mock_invoices_repository.create.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        checkout_service.checkout(
            cart_id=1,
            user_id=10,
            billing_address_id=3,
            payment_method="SINPE",
            payment_reference="SINPE-001"
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


def test_checkout_rolls_back_if_invoice_product_creation_fails(
    checkout_service,
    mock_carts_repository,
    mock_products_repository,
    mock_billing_addresses_repository,
    mock_invoices_repository,
    mock_invoice_products_repository,
    mock_session
):
    cart = create_active_cart()

    product = create_product()

    billing_address = create_billing_address()

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    mock_billing_addresses_repository.get_by_id.return_value = (
        billing_address
    )

    def assign_invoice_id(invoice):
        invoice.id = 100

    mock_invoices_repository.create.side_effect = (
        assign_invoice_id
    )

    mock_invoice_products_repository.create.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        checkout_service.checkout(
            cart_id=1,
            user_id=10,
            billing_address_id=3,
            payment_method="SINPE",
            payment_reference="SINPE-001"
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


def test_checkout_rolls_back_if_payment_creation_fails(
    checkout_service,
    mock_carts_repository,
    mock_products_repository,
    mock_billing_addresses_repository,
    mock_invoices_repository,
    mock_payments_repository,
    mock_session
):
    cart = create_active_cart()

    product = create_product()

    billing_address = create_billing_address()

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    mock_billing_addresses_repository.get_by_id.return_value = (
        billing_address
    )

    def assign_invoice_id(invoice):
        invoice.id = 100

    mock_invoices_repository.create.side_effect = (
        assign_invoice_id
    )

    mock_payments_repository.create.side_effect = (
        Exception("Payment error")
    )

    with pytest.raises(
        Exception,
        match="Payment error"
    ):
        checkout_service.checkout(
            cart_id=1,
            user_id=10,
            billing_address_id=3,
            payment_method="SINPE",
            payment_reference="SINPE-001"
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


def test_checkout_rolls_back_if_commit_fails(
    checkout_service,
    mock_carts_repository,
    mock_products_repository,
    mock_billing_addresses_repository,
    mock_invoices_repository,
    mock_session
):
    cart = create_active_cart()

    product = create_product()

    billing_address = create_billing_address()

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    mock_billing_addresses_repository.get_by_id.return_value = (
        billing_address
    )

    def assign_invoice_id(invoice):
        invoice.id = 100

    mock_invoices_repository.create.side_effect = (
        assign_invoice_id
    )

    mock_session.commit.side_effect = (
        Exception("Commit error")
    )

    with pytest.raises(
        Exception,
        match="Commit error"
    ):
        checkout_service.checkout(
            cart_id=1,
            user_id=10,
            billing_address_id=3,
            payment_method="SINPE",
            payment_reference="SINPE-001"
        )

    mock_session.rollback.assert_called_once_with()


# ============================================================
# CACHE INVALIDATION
# ============================================================

def test_checkout_invalidates_all_product_cache_keys(
    checkout_service,
    mock_cache_manager,
    mock_carts_repository,
    mock_products_repository,
    mock_billing_addresses_repository,
    mock_invoices_repository
):
    item_1 = create_cart_item(
        product_id=5,
        quantity=1
    )

    item_2 = create_cart_item(
        product_id=6,
        quantity=1
    )

    cart = create_active_cart(
        cart_products=[
            item_1,
            item_2
        ]
    )

    product_1 = create_product(
        product_id=5
    )

    product_2 = create_product(
        product_id=6
    )

    billing_address = create_billing_address()

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.side_effect = [
        product_1,
        product_2
    ]

    mock_billing_addresses_repository.get_by_id.return_value = (
        billing_address
    )

    def assign_invoice_id(invoice):
        invoice.id = 100

    mock_invoices_repository.create.side_effect = (
        assign_invoice_id
    )

    checkout_service.checkout(
        cart_id=1,
        user_id=10,
        billing_address_id=3,
        payment_method="SINPE",
        payment_reference="SINPE-001"
    )

    assert (
        mock_cache_manager.delete_data.call_count
        == 3
    )

    mock_cache_manager.delete_data.assert_any_call(
        "product:5"
    )

    mock_cache_manager.delete_data.assert_any_call(
        "product:6"
    )

    mock_cache_manager.delete_data.assert_any_call(
        "products:all"
    )


# ============================================================
# INVOICE NUMBER
# ============================================================

def test_generate_invoice_number_format():
    invoice_number = (
        CheckoutService._generate_invoice_number()
    )

    assert invoice_number.startswith(
        "INV-"
    )

    assert len(invoice_number) == 16


def test_generate_invoice_numbers_are_unique():
    invoice_1 = (
        CheckoutService._generate_invoice_number()
    )

    invoice_2 = (
        CheckoutService._generate_invoice_number()
    )

    assert invoice_1 != invoice_2