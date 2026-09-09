from decimal import Decimal
from unittest.mock import Mock

import pytest

from services.cart_service import CartService


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_session():
    return Mock()


@pytest.fixture
def mock_carts_repository():
    return Mock()


@pytest.fixture
def mock_products_repository():
    return Mock()


@pytest.fixture
def cart_service(
    mock_session,
    mock_carts_repository,
    mock_products_repository
):
    service = CartService(
        mock_session
    )

    service.carts_repository = (
        mock_carts_repository
    )

    service.products_repository = (
        mock_products_repository
    )

    return service


# ============================================================
# GET OR CREATE ACTIVE CART
# ============================================================

def test_get_or_create_active_cart_returns_existing_cart(
    cart_service,
    mock_carts_repository,
    mock_session
):
    cart = Mock()
    cart.id = 1
    cart.user_id = 10
    cart.status = "ACTIVE"

    mock_carts_repository.get_active_cart_by_user.return_value = (
        cart
    )

    result = cart_service.get_or_create_active_cart(
        user_id=10
    )

    assert result == cart

    mock_carts_repository.get_active_cart_by_user.assert_called_once_with(
        10
    )

    mock_carts_repository.create.assert_not_called()
    mock_session.commit.assert_not_called()


def test_get_or_create_active_cart_creates_new_cart(
    cart_service,
    mock_carts_repository,
    mock_session
):
    mock_carts_repository.get_active_cart_by_user.return_value = (
        None
    )

    result = cart_service.get_or_create_active_cart(
        user_id=10
    )

    assert result.user_id == 10
    assert result.status == "ACTIVE"

    mock_carts_repository.create.assert_called_once_with(
        result
    )

    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_get_or_create_active_cart_rolls_back_on_error(
    cart_service,
    mock_carts_repository,
    mock_session
):
    mock_carts_repository.get_active_cart_by_user.return_value = (
        None
    )

    mock_carts_repository.create.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        cart_service.get_or_create_active_cart(
            user_id=10
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


# ============================================================
# GET CART
# ============================================================

def test_get_cart_success(
    cart_service,
    mock_carts_repository
):
    cart = Mock()
    cart.id = 1
    cart.user_id = 10

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    result = cart_service.get_cart(
        cart_id=1,
        user_id=10
    )

    assert result == cart

    mock_carts_repository.get_cart_with_products.assert_called_once_with(
        1
    )


def test_get_cart_not_found(
    cart_service,
    mock_carts_repository
):
    mock_carts_repository.get_cart_with_products.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Cart not found."
    ):
        cart_service.get_cart(
            cart_id=999,
            user_id=10
        )


def test_get_cart_wrong_user(
    cart_service,
    mock_carts_repository
):
    cart = Mock()
    cart.user_id = 20

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    with pytest.raises(
        PermissionError,
        match="You do not have access to this cart."
    ):
        cart_service.get_cart(
            cart_id=1,
            user_id=10
        )


# ============================================================
# GET USER CARTS
# ============================================================

def test_get_user_carts(
    cart_service,
    mock_carts_repository
):
    carts = [
        Mock(),
        Mock()
    ]

    mock_carts_repository.get_carts_by_user.return_value = (
        carts
    )

    result = cart_service.get_user_carts(
        user_id=10
    )

    assert result == carts

    mock_carts_repository.get_carts_by_user.assert_called_once_with(
        10
    )


# ============================================================
# ADD PRODUCT
# ============================================================

def test_add_product_success_new_item(
    cart_service,
    mock_carts_repository,
    mock_products_repository,
    mock_session
):
    cart = Mock()
    cart.id = 1
    cart.user_id = 10
    cart.status = "ACTIVE"

    product = Mock()
    product.id = 5
    product.is_active = True
    product.stock = 20
    product.price = Decimal("12.50")

    refreshed_cart = Mock()

    mock_carts_repository.get_cart_with_products.side_effect = [
        cart,
        refreshed_cart
    ]

    mock_products_repository.get_by_id.return_value = (
        product
    )

    mock_carts_repository.get_cart_product.return_value = (
        None
    )

    result = cart_service.add_product(
        cart_id=1,
        product_id=5,
        quantity=3,
        user_id=10
    )

    assert result == refreshed_cart

    mock_carts_repository.add_cart_product.assert_called_once()

    created_cart_product = (
        mock_carts_repository
        .add_cart_product
        .call_args[0][0]
    )

    assert created_cart_product.cart_id == 1
    assert created_cart_product.product_id == 5
    assert created_cart_product.quantity == 3
    assert created_cart_product.price_at_added == Decimal(
        "12.50"
    )

    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_add_product_increases_existing_quantity(
    cart_service,
    mock_carts_repository,
    mock_products_repository,
    mock_session
):
    cart = Mock()
    cart.id = 1
    cart.user_id = 10
    cart.status = "ACTIVE"

    product = Mock()
    product.id = 5
    product.is_active = True
    product.stock = 20

    cart_product = Mock()
    cart_product.quantity = 4

    refreshed_cart = Mock()

    mock_carts_repository.get_cart_with_products.side_effect = [
        cart,
        refreshed_cart
    ]

    mock_products_repository.get_by_id.return_value = (
        product
    )

    mock_carts_repository.get_cart_product.return_value = (
        cart_product
    )

    result = cart_service.add_product(
        cart_id=1,
        product_id=5,
        quantity=3,
        user_id=10
    )

    assert result == refreshed_cart
    assert cart_product.quantity == 7

    mock_carts_repository.add_cart_product.assert_not_called()
    mock_session.commit.assert_called_once_with()


def test_add_product_to_inactive_cart(
    cart_service,
    mock_carts_repository,
    mock_products_repository
):
    cart = Mock()
    cart.user_id = 10
    cart.status = "COMPLETED"

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    with pytest.raises(
        ValueError,
        match="Only active carts can be modified."
    ):
        cart_service.add_product(
            cart_id=1,
            product_id=5,
            quantity=1,
            user_id=10
        )

    mock_products_repository.get_by_id.assert_not_called()


def test_add_product_not_found(
    cart_service,
    mock_carts_repository,
    mock_products_repository
):
    cart = Mock()
    cart.user_id = 10
    cart.status = "ACTIVE"

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Product not found."
    ):
        cart_service.add_product(
            cart_id=1,
            product_id=999,
            quantity=1,
            user_id=10
        )


def test_add_product_inactive_product(
    cart_service,
    mock_carts_repository,
    mock_products_repository
):
    cart = Mock()
    cart.user_id = 10
    cart.status = "ACTIVE"

    product = Mock()
    product.is_active = False

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    with pytest.raises(
        ValueError,
        match="Product is not available."
    ):
        cart_service.add_product(
            cart_id=1,
            product_id=5,
            quantity=1,
            user_id=10
        )


def test_add_product_insufficient_stock(
    cart_service,
    mock_carts_repository,
    mock_products_repository
):
    cart = Mock()
    cart.user_id = 10
    cart.status = "ACTIVE"

    product = Mock()
    product.is_active = True
    product.stock = 2

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    with pytest.raises(
        ValueError,
        match="Insufficient product stock."
    ):
        cart_service.add_product(
            cart_id=1,
            product_id=5,
            quantity=3,
            user_id=10
        )


def test_add_product_existing_item_exceeds_stock(
    cart_service,
    mock_carts_repository,
    mock_products_repository,
    mock_session
):
    cart = Mock()
    cart.id = 1
    cart.user_id = 10
    cart.status = "ACTIVE"

    product = Mock()
    product.id = 5
    product.is_active = True
    product.stock = 5

    cart_product = Mock()
    cart_product.quantity = 4

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    mock_carts_repository.get_cart_product.return_value = (
        cart_product
    )

    with pytest.raises(
        ValueError,
        match="Insufficient product stock."
    ):
        cart_service.add_product(
            cart_id=1,
            product_id=5,
            quantity=2,
            user_id=10
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


def test_add_product_rolls_back_on_repository_error(
    cart_service,
    mock_carts_repository,
    mock_products_repository,
    mock_session
):
    cart = Mock()
    cart.id = 1
    cart.user_id = 10
    cart.status = "ACTIVE"

    product = Mock()
    product.id = 5
    product.is_active = True
    product.stock = 20
    product.price = Decimal("12.50")

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    mock_carts_repository.get_cart_product.return_value = (
        None
    )

    mock_carts_repository.add_cart_product.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        cart_service.add_product(
            cart_id=1,
            product_id=5,
            quantity=2,
            user_id=10
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


# ============================================================
# UPDATE PRODUCT QUANTITY
# ============================================================

def test_update_product_quantity_success(
    cart_service,
    mock_carts_repository,
    mock_products_repository,
    mock_session
):
    cart = Mock()
    cart.id = 1
    cart.user_id = 10
    cart.status = "ACTIVE"

    product = Mock()
    product.id = 5
    product.is_active = True
    product.stock = 20

    cart_product = Mock()
    cart_product.quantity = 3

    refreshed_cart = Mock()

    mock_carts_repository.get_cart_with_products.side_effect = [
        cart,
        refreshed_cart
    ]

    mock_products_repository.get_by_id.return_value = (
        product
    )

    mock_carts_repository.get_cart_product.return_value = (
        cart_product
    )

    result = cart_service.update_product_quantity(
        cart_id=1,
        product_id=5,
        quantity=8,
        user_id=10
    )

    assert result == refreshed_cart
    assert cart_product.quantity == 8

    mock_session.flush.assert_called_once_with()
    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_update_product_quantity_product_not_in_cart(
    cart_service,
    mock_carts_repository,
    mock_products_repository
):
    cart = Mock()
    cart.id = 1
    cart.user_id = 10
    cart.status = "ACTIVE"

    product = Mock()
    product.is_active = True
    product.stock = 20

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    mock_carts_repository.get_cart_product.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Product is not in the cart."
    ):
        cart_service.update_product_quantity(
            cart_id=1,
            product_id=5,
            quantity=5,
            user_id=10
        )


def test_update_product_quantity_insufficient_stock(
    cart_service,
    mock_carts_repository,
    mock_products_repository
):
    cart = Mock()
    cart.user_id = 10
    cart.status = "ACTIVE"

    product = Mock()
    product.is_active = True
    product.stock = 5

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    with pytest.raises(
        ValueError,
        match="Insufficient product stock."
    ):
        cart_service.update_product_quantity(
            cart_id=1,
            product_id=5,
            quantity=6,
            user_id=10
        )


def test_update_product_quantity_rolls_back_on_error(
    cart_service,
    mock_carts_repository,
    mock_products_repository,
    mock_session
):
    cart = Mock()
    cart.id = 1
    cart.user_id = 10
    cart.status = "ACTIVE"

    product = Mock()
    product.is_active = True
    product.stock = 20

    cart_product = Mock()
    cart_product.quantity = 2

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_products_repository.get_by_id.return_value = (
        product
    )

    mock_carts_repository.get_cart_product.return_value = (
        cart_product
    )

    mock_session.flush.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        cart_service.update_product_quantity(
            cart_id=1,
            product_id=5,
            quantity=5,
            user_id=10
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


# ============================================================
# REMOVE PRODUCT
# ============================================================

def test_remove_product_success(
    cart_service,
    mock_carts_repository,
    mock_session
):
    cart = Mock()
    cart.id = 1
    cart.user_id = 10
    cart.status = "ACTIVE"

    cart_product = Mock()
    refreshed_cart = Mock()

    mock_carts_repository.get_cart_with_products.side_effect = [
        cart,
        refreshed_cart
    ]

    mock_carts_repository.get_cart_product.return_value = (
        cart_product
    )

    result = cart_service.remove_product(
        cart_id=1,
        product_id=5,
        user_id=10
    )

    assert result == refreshed_cart

    mock_carts_repository.delete_cart_product.assert_called_once_with(
        cart_product
    )

    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_remove_product_not_in_cart(
    cart_service,
    mock_carts_repository
):
    cart = Mock()
    cart.id = 1
    cart.user_id = 10
    cart.status = "ACTIVE"

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_carts_repository.get_cart_product.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Product is not in the cart."
    ):
        cart_service.remove_product(
            cart_id=1,
            product_id=5,
            user_id=10
        )


def test_remove_product_rolls_back_on_error(
    cart_service,
    mock_carts_repository,
    mock_session
):
    cart = Mock()
    cart.id = 1
    cart.user_id = 10
    cart.status = "ACTIVE"

    cart_product = Mock()

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_carts_repository.get_cart_product.return_value = (
        cart_product
    )

    mock_carts_repository.delete_cart_product.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        cart_service.remove_product(
            cart_id=1,
            product_id=5,
            user_id=10
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


# ============================================================
# ABANDON CART
# ============================================================

def test_abandon_cart_success(
    cart_service,
    mock_carts_repository,
    mock_session
):
    cart = Mock()
    cart.id = 1
    cart.user_id = 10
    cart.status = "ACTIVE"

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    result = cart_service.abandon_cart(
        cart_id=1,
        user_id=10
    )

    assert result == cart
    assert cart.status == "ABANDONED"

    mock_carts_repository.update.assert_called_once_with(
        cart
    )

    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_abandon_non_active_cart(
    cart_service,
    mock_carts_repository,
    mock_session
):
    cart = Mock()
    cart.user_id = 10
    cart.status = "COMPLETED"

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    with pytest.raises(
        ValueError,
        match="Only active carts can be modified."
    ):
        cart_service.abandon_cart(
            cart_id=1,
            user_id=10
        )

    mock_carts_repository.update.assert_not_called()
    mock_session.commit.assert_not_called()


def test_abandon_cart_rolls_back_on_error(
    cart_service,
    mock_carts_repository,
    mock_session
):
    cart = Mock()
    cart.user_id = 10
    cart.status = "ACTIVE"

    mock_carts_repository.get_cart_with_products.return_value = (
        cart
    )

    mock_carts_repository.update.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        cart_service.abandon_cart(
            cart_id=1,
            user_id=10
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


# ============================================================
# VALIDATE ACTIVE CART
# ============================================================

def test_validate_active_cart_success():
    cart = Mock()
    cart.status = "ACTIVE"

    CartService._validate_active_cart(
        cart
    )


def test_validate_active_cart_invalid_status():
    cart = Mock()
    cart.status = "COMPLETED"

    with pytest.raises(
        ValueError,
        match="Only active carts can be modified."
    ):
        CartService._validate_active_cart(
            cart
        )


# ============================================================
# VALIDATE QUANTITY
# ============================================================

def test_validate_quantity_success():
    CartService._validate_quantity(
        5
    )


def test_validate_quantity_zero():
    with pytest.raises(
        ValueError,
        match="Quantity must be greater than zero."
    ):
        CartService._validate_quantity(
            0
        )


def test_validate_quantity_negative():
    with pytest.raises(
        ValueError,
        match="Quantity must be greater than zero."
    ):
        CartService._validate_quantity(
            -1
        )


def test_validate_quantity_float():
    with pytest.raises(
        ValueError,
        match="Quantity must be an integer."
    ):
        CartService._validate_quantity(
            2.5
        )


def test_validate_quantity_string():
    with pytest.raises(
        ValueError,
        match="Quantity must be an integer."
    ):
        CartService._validate_quantity(
            "5"
        )


def test_validate_quantity_boolean():
    with pytest.raises(
        ValueError,
        match="Quantity must be an integer."
    ):
        CartService._validate_quantity(
            True
        )