from decimal import Decimal
from unittest.mock import Mock

import pytest

from services.product_service import ProductService


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_session():
    """
    Creates a fake SQLAlchemy session.
    """
    return Mock()


@pytest.fixture
def mock_repository():
    """
    Creates a fake ProductsRepository.
    """
    return Mock()


@pytest.fixture
def product_service(
    mock_session,
    mock_repository
):
    """
    Creates ProductService using a mocked session
    and replaces the real repository with a mock.
    """
    service = ProductService(
        mock_session
    )

    service.products_repository = (
        mock_repository
    )

    return service


# ============================================================
# GET ALL PRODUCTS
# ============================================================

def test_get_all_products(
    product_service,
    mock_repository
):
    products = [
        Mock(),
        Mock()
    ]

    mock_repository.get_all.return_value = (
        products
    )

    result = (
        product_service.get_all_products()
    )

    assert result == products

    mock_repository.get_all.assert_called_once_with()


# ============================================================
# GET PRODUCT BY ID
# ============================================================

def test_get_product_by_id_success(
    product_service,
    mock_repository
):
    product = Mock()
    product.id = 1

    mock_repository.get_by_id.return_value = (
        product
    )

    result = (
        product_service.get_product_by_id(1)
    )

    assert result == product

    mock_repository.get_by_id.assert_called_once_with(
        1
    )


def test_get_product_by_id_not_found(
    product_service,
    mock_repository
):
    mock_repository.get_by_id.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Product not found."
    ):
        product_service.get_product_by_id(
            999
        )

    mock_repository.get_by_id.assert_called_once_with(
        999
    )


# ============================================================
# CREATE PRODUCT
# ============================================================

def test_create_product_success(
    product_service,
    mock_repository,
    mock_session
):
    mock_repository.get_by_name.return_value = (
        None
    )

    data = {
        "name": "Dog Food",
        "price": 25.50,
        "stock": 10
    }

    product = product_service.create_product(
        data=data,
        user_id=1
    )

    assert product.name == "Dog Food"
    assert product.price == Decimal("25.5")
    assert product.stock == 10
    assert product.created_by == 1

    mock_repository.get_by_name.assert_called_once_with(
        "Dog Food"
    )

    mock_repository.create.assert_called_once_with(
        product
    )

    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_create_product_duplicate_name(
    product_service,
    mock_repository,
    mock_session
):
    existing_product = Mock()

    mock_repository.get_by_name.return_value = (
        existing_product
    )

    data = {
        "name": "Dog Food",
        "price": 25.50,
        "stock": 10
    }

    with pytest.raises(
        ValueError,
        match=(
            "A product with this name "
            "already exists."
        )
    ):
        product_service.create_product(
            data=data,
            user_id=1
        )

    mock_repository.create.assert_not_called()
    mock_session.commit.assert_not_called()


def test_create_product_negative_price(
    product_service,
    mock_repository,
    mock_session
):
    mock_repository.get_by_name.return_value = (
        None
    )

    data = {
        "name": "Dog Food",
        "price": -10,
        "stock": 10
    }

    with pytest.raises(
        ValueError,
        match="Price cannot be negative."
    ):
        product_service.create_product(
            data=data,
            user_id=1
        )

    mock_repository.create.assert_not_called()
    mock_session.commit.assert_not_called()


def test_create_product_negative_stock(
    product_service,
    mock_repository,
    mock_session
):
    mock_repository.get_by_name.return_value = (
        None
    )

    data = {
        "name": "Dog Food",
        "price": 20,
        "stock": -1
    }

    with pytest.raises(
        ValueError,
        match="Stock cannot be negative."
    ):
        product_service.create_product(
            data=data,
            user_id=1
        )

    mock_repository.create.assert_not_called()
    mock_session.commit.assert_not_called()


def test_create_product_rollback_on_repository_error(
    product_service,
    mock_repository,
    mock_session
):
    mock_repository.get_by_name.return_value = (
        None
    )

    mock_repository.create.side_effect = (
        Exception("Database error")
    )

    data = {
        "name": "Dog Food",
        "price": 25.50,
        "stock": 10
    }

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        product_service.create_product(
            data=data,
            user_id=1
        )

    mock_session.commit.assert_not_called()

    mock_session.rollback.assert_called_once_with()


# ============================================================
# UPDATE PRODUCT
# ============================================================

def test_update_product_success(
    product_service,
    mock_repository,
    mock_session
):
    product = Mock()

    product.id = 1
    product.name = "Old Name"
    product.price = Decimal("10.00")
    product.stock = 5
    product.is_active = True
    product.updated_by = None

    mock_repository.get_by_id.return_value = (
        product
    )

    mock_repository.get_by_name.return_value = (
        None
    )

    data = {
        "name": "New Dog Food",
        "price": 30.50,
        "stock": 20,
        "is_active": True
    }

    result = product_service.update_product(
        product_id=1,
        data=data,
        user_id=5
    )

    assert result == product

    assert product.name == "New Dog Food"
    assert product.price == Decimal("30.5")
    assert product.stock == 20
    assert product.is_active is True
    assert product.updated_by == 5

    mock_repository.get_by_id.assert_called_once_with(
        1
    )

    mock_repository.get_by_name.assert_called_once_with(
        "New Dog Food"
    )

    mock_repository.update.assert_called_once_with(
        product
    )

    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_update_product_partial_update(
    product_service,
    mock_repository,
    mock_session
):
    product = Mock()

    product.id = 1
    product.name = "Dog Food"
    product.price = Decimal("20.00")
    product.stock = 10
    product.is_active = True

    mock_repository.get_by_id.return_value = (
        product
    )

    data = {
        "stock": 25
    }

    result = product_service.update_product(
        product_id=1,
        data=data,
        user_id=5
    )

    assert result.stock == 25
    assert result.name == "Dog Food"
    assert result.price == Decimal("20.00")
    assert result.updated_by == 5

    mock_repository.get_by_name.assert_not_called()

    mock_repository.update.assert_called_once_with(
        product
    )

    mock_session.commit.assert_called_once_with()


def test_update_product_invalid_field(
    product_service,
    mock_repository,
    mock_session
):
    product = Mock()
    product.id = 1

    mock_repository.get_by_id.return_value = (
        product
    )

    data = {
        "description": "Invalid field"
    }

    with pytest.raises(
        ValueError,
        match="Fields cannot be updated"
    ):
        product_service.update_product(
            product_id=1,
            data=data,
            user_id=5
        )

    mock_repository.update.assert_not_called()
    mock_session.commit.assert_not_called()


def test_update_product_empty_name(
    product_service,
    mock_repository,
    mock_session
):
    product = Mock()
    product.id = 1

    mock_repository.get_by_id.return_value = (
        product
    )

    data = {
        "name": "   "
    }

    with pytest.raises(
        ValueError,
        match="Product name cannot be empty."
    ):
        product_service.update_product(
            product_id=1,
            data=data,
            user_id=5
        )

    mock_repository.update.assert_not_called()
    mock_session.commit.assert_not_called()


def test_update_product_duplicate_name(
    product_service,
    mock_repository,
    mock_session
):
    product = Mock()
    product.id = 1
    product.name = "Dog Food"

    other_product = Mock()
    other_product.id = 2
    other_product.name = "Cat Food"

    mock_repository.get_by_id.return_value = (
        product
    )

    mock_repository.get_by_name.return_value = (
        other_product
    )

    data = {
        "name": "Cat Food"
    }

    with pytest.raises(
        ValueError,
        match=(
            "A product with this name "
            "already exists."
        )
    ):
        product_service.update_product(
            product_id=1,
            data=data,
            user_id=5
        )

    mock_repository.update.assert_not_called()
    mock_session.commit.assert_not_called()


def test_update_product_same_name_allowed(
    product_service,
    mock_repository,
    mock_session
):
    product = Mock()
    product.id = 1
    product.name = "Dog Food"

    mock_repository.get_by_id.return_value = (
        product
    )

    mock_repository.get_by_name.return_value = (
        product
    )

    data = {
        "name": "Dog Food"
    }

    result = product_service.update_product(
        product_id=1,
        data=data,
        user_id=5
    )

    assert result.name == "Dog Food"
    assert result.updated_by == 5

    mock_repository.update.assert_called_once_with(
        product
    )

    mock_session.commit.assert_called_once_with()


def test_update_product_invalid_is_active(
    product_service,
    mock_repository,
    mock_session
):
    product = Mock()
    product.id = 1

    mock_repository.get_by_id.return_value = (
        product
    )

    data = {
        "is_active": "yes"
    }

    with pytest.raises(
        ValueError,
        match="is_active must be a boolean."
    ):
        product_service.update_product(
            product_id=1,
            data=data,
            user_id=5
        )

    mock_repository.update.assert_not_called()
    mock_session.commit.assert_not_called()


def test_update_product_not_found(
    product_service,
    mock_repository,
    mock_session
):
    mock_repository.get_by_id.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Product not found."
    ):
        product_service.update_product(
            product_id=999,
            data={"stock": 10},
            user_id=5
        )

    mock_repository.update.assert_not_called()
    mock_session.commit.assert_not_called()


def test_update_product_rollback_on_repository_error(
    product_service,
    mock_repository,
    mock_session
):
    product = Mock()

    product.id = 1
    product.stock = 10

    mock_repository.get_by_id.return_value = (
        product
    )

    mock_repository.update.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        product_service.update_product(
            product_id=1,
            data={"stock": 20},
            user_id=5
        )

    mock_session.commit.assert_not_called()

    mock_session.rollback.assert_called_once_with()


# ============================================================
# DELETE PRODUCT
# ============================================================

def test_delete_product_success(
    product_service,
    mock_repository,
    mock_session
):
    product = Mock()

    product.id = 1
    product.is_active = True
    product.updated_by = None

    mock_repository.get_by_id.return_value = (
        product
    )

    result = product_service.delete_product(
        product_id=1,
        user_id=5
    )

    assert result is None
    assert product.is_active is False
    assert product.updated_by == 5

    mock_repository.update.assert_called_once_with(
        product
    )

    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_delete_product_not_found(
    product_service,
    mock_repository,
    mock_session
):
    mock_repository.get_by_id.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Product not found."
    ):
        product_service.delete_product(
            product_id=999,
            user_id=5
        )

    mock_repository.update.assert_not_called()
    mock_session.commit.assert_not_called()


def test_delete_product_rollback_on_repository_error(
    product_service,
    mock_repository,
    mock_session
):
    product = Mock()

    product.id = 1
    product.is_active = True

    mock_repository.get_by_id.return_value = (
        product
    )

    mock_repository.update.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        product_service.delete_product(
            product_id=1,
            user_id=5
        )

    mock_session.commit.assert_not_called()

    mock_session.rollback.assert_called_once_with()


# ============================================================
# PRICE VALIDATION
# ============================================================

def test_validate_price_success():
    result = ProductService._validate_price(
        25.50
    )

    assert isinstance(result, Decimal)
    assert result == Decimal("25.5")


def test_validate_price_from_string():
    result = ProductService._validate_price(
        "19.99"
    )

    assert isinstance(result, Decimal)
    assert result == Decimal("19.99")


def test_validate_price_zero():
    result = ProductService._validate_price(
        0
    )

    assert result == Decimal("0")


def test_validate_price_negative():
    with pytest.raises(
        ValueError,
        match="Price cannot be negative."
    ):
        ProductService._validate_price(
            -10
        )


def test_validate_price_invalid_string():
    with pytest.raises(
        ValueError,
        match="Price must be a valid number."
    ):
        ProductService._validate_price(
            "invalid"
        )


def test_validate_price_none():
    with pytest.raises(
        ValueError,
        match="Price must be a valid number."
    ):
        ProductService._validate_price(
            None
        )


# ============================================================
# STOCK VALIDATION
# ============================================================

def test_validate_stock_success():
    result = ProductService._validate_stock(
        10
    )

    assert result == 10


def test_validate_stock_zero():
    result = ProductService._validate_stock(
        0
    )

    assert result == 0


def test_validate_stock_negative():
    with pytest.raises(
        ValueError,
        match="Stock cannot be negative."
    ):
        ProductService._validate_stock(
            -1
        )


def test_validate_stock_float():
    with pytest.raises(
        ValueError,
        match="Stock must be an integer."
    ):
        ProductService._validate_stock(
            10.5
        )


def test_validate_stock_string():
    with pytest.raises(
        ValueError,
        match="Stock must be an integer."
    ):
        ProductService._validate_stock(
            "10"
        )


def test_validate_stock_boolean():
    with pytest.raises(
        ValueError,
        match="Stock must be an integer."
    ):
        ProductService._validate_stock(
            True
        )