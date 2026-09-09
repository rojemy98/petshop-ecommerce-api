from unittest.mock import Mock

import pytest

from services.billing_address_service import BillingAddressService


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
def billing_address_service(
    mock_session,
    mock_repository
):
    service = BillingAddressService(
        mock_session
    )

    service.repository = (
        mock_repository
    )

    return service


# ============================================================
# Helper
# ============================================================

def create_address(
    address_id=1,
    user_id=10,
    address="San Rafael",
    city="Heredia",
    province="Heredia",
    postal_code=40501,
    country="Costa Rica"
):
    billing_address = Mock()

    billing_address.id = address_id
    billing_address.user_id = user_id
    billing_address.address = address
    billing_address.city = city
    billing_address.province = province
    billing_address.postal_code = postal_code
    billing_address.country = country

    return billing_address


# ============================================================
# GET USER ADDRESSES
# ============================================================

def test_get_user_addresses(
    billing_address_service,
    mock_repository
):
    addresses = [
        create_address(address_id=1),
        create_address(address_id=2)
    ]

    mock_repository.get_by_user_id.return_value = (
        addresses
    )

    result = (
        billing_address_service
        .get_user_addresses(
            user_id=10
        )
    )

    assert result == addresses

    mock_repository.get_by_user_id.assert_called_once_with(
        10
    )


# ============================================================
# GET ADDRESS
# ============================================================

def test_get_address_success(
    billing_address_service,
    mock_repository
):
    address = create_address(
        address_id=1,
        user_id=10
    )

    mock_repository.get_by_id.return_value = (
        address
    )

    result = (
        billing_address_service
        .get_address(
            address_id=1,
            user_id=10
        )
    )

    assert result == address

    mock_repository.get_by_id.assert_called_once_with(
        1
    )


def test_get_address_not_found(
    billing_address_service,
    mock_repository
):
    mock_repository.get_by_id.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Billing address not found."
    ):
        billing_address_service.get_address(
            address_id=999,
            user_id=10
        )


def test_get_address_wrong_user(
    billing_address_service,
    mock_repository
):
    address = create_address(
        address_id=1,
        user_id=20
    )

    mock_repository.get_by_id.return_value = (
        address
    )

    with pytest.raises(
        PermissionError,
        match=(
            "You do not have access to this "
            "billing address."
        )
    ):
        billing_address_service.get_address(
            address_id=1,
            user_id=10
        )


# ============================================================
# CREATE ADDRESS
# ============================================================

def test_create_address_success(
    billing_address_service,
    mock_repository,
    mock_session
):
    data = {
        "address": "  San Rafael  ",
        "city": "  Heredia  ",
        "province": "  Heredia  ",
        "postal_code": 40501,
        "country": "  Costa Rica  "
    }

    result = (
        billing_address_service
        .create_address(
            data=data,
            user_id=10
        )
    )

    assert result.user_id == 10
    assert result.address == "San Rafael"
    assert result.city == "Heredia"
    assert result.province == "Heredia"
    assert result.postal_code == 40501
    assert result.country == "Costa Rica"

    mock_repository.create.assert_called_once_with(
        result
    )

    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_create_address_rolls_back_on_error(
    billing_address_service,
    mock_repository,
    mock_session
):
    data = {
        "address": "San Rafael",
        "city": "Heredia",
        "province": "Heredia",
        "postal_code": 40501,
        "country": "Costa Rica"
    }

    mock_repository.create.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        billing_address_service.create_address(
            data=data,
            user_id=10
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


# ============================================================
# UPDATE ADDRESS
# ============================================================

def test_update_address_success(
    billing_address_service,
    mock_repository,
    mock_session
):
    address = create_address()

    mock_repository.get_by_id.return_value = (
        address
    )

    data = {
        "address": "  Santo Domingo  ",
        "city": "  Santo Domingo  ",
        "province": "  Heredia  ",
        "postal_code": 40301,
        "country": "  Costa Rica  "
    }

    result = (
        billing_address_service
        .update_address(
            address_id=1,
            data=data,
            user_id=10
        )
    )

    assert result.address == "Santo Domingo"
    assert result.city == "Santo Domingo"
    assert result.province == "Heredia"
    assert result.postal_code == 40301
    assert result.country == "Costa Rica"

    mock_repository.update.assert_called_once_with(
        address
    )

    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_update_address_partial_update(
    billing_address_service,
    mock_repository,
    mock_session
):
    address = create_address(
        city="Heredia"
    )

    mock_repository.get_by_id.return_value = (
        address
    )

    result = (
        billing_address_service
        .update_address(
            address_id=1,
            data={
                "city": "  Alajuela  "
            },
            user_id=10
        )
    )

    assert result.city == "Alajuela"

    mock_repository.update.assert_called_once_with(
        address
    )

    mock_session.commit.assert_called_once_with()


def test_update_address_invalid_field(
    billing_address_service,
    mock_repository
):
    address = create_address()

    mock_repository.get_by_id.return_value = (
        address
    )

    with pytest.raises(
        ValueError,
        match="Fields cannot be updated: email."
    ):
        billing_address_service.update_address(
            address_id=1,
            data={
                "email": "test@example.com"
            },
            user_id=10
        )


@pytest.mark.parametrize(
    "field",
    [
        "address",
        "city",
        "province",
        "country"
    ]
)
def test_update_address_empty_string(
    billing_address_service,
    mock_repository,
    field
):
    address = create_address()

    mock_repository.get_by_id.return_value = (
        address
    )

    with pytest.raises(
        ValueError,
        match=f"{field} cannot be empty."
    ):
        billing_address_service.update_address(
            address_id=1,
            data={
                field: "   "
            },
            user_id=10
        )


def test_update_address_postal_code(
    billing_address_service,
    mock_repository
):
    address = create_address(
        postal_code=40501
    )

    mock_repository.get_by_id.return_value = (
        address
    )

    result = (
        billing_address_service
        .update_address(
            address_id=1,
            data={
                "postal_code": 40101
            },
            user_id=10
        )
    )

    assert result.postal_code == 40101


def test_update_address_not_found(
    billing_address_service,
    mock_repository
):
    mock_repository.get_by_id.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Billing address not found."
    ):
        billing_address_service.update_address(
            address_id=999,
            data={
                "city": "Heredia"
            },
            user_id=10
        )


def test_update_address_wrong_user(
    billing_address_service,
    mock_repository
):
    address = create_address(
        user_id=20
    )

    mock_repository.get_by_id.return_value = (
        address
    )

    with pytest.raises(
        PermissionError,
        match=(
            "You do not have access to this "
            "billing address."
        )
    ):
        billing_address_service.update_address(
            address_id=1,
            data={
                "city": "Heredia"
            },
            user_id=10
        )


def test_update_address_rolls_back_on_error(
    billing_address_service,
    mock_repository,
    mock_session
):
    address = create_address()

    mock_repository.get_by_id.return_value = (
        address
    )

    mock_repository.update.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        billing_address_service.update_address(
            address_id=1,
            data={
                "city": "Alajuela"
            },
            user_id=10
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


# ============================================================
# DELETE ADDRESS
# ============================================================

def test_delete_address_success(
    billing_address_service,
    mock_repository,
    mock_session
):
    address = create_address()

    mock_repository.get_by_id.return_value = (
        address
    )

    result = (
        billing_address_service
        .delete_address(
            address_id=1,
            user_id=10
        )
    )

    assert result is None

    mock_repository.delete.assert_called_once_with(
        address
    )

    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_delete_address_not_found(
    billing_address_service,
    mock_repository
):
    mock_repository.get_by_id.return_value = (
        None
    )

    with pytest.raises(
        LookupError,
        match="Billing address not found."
    ):
        billing_address_service.delete_address(
            address_id=999,
            user_id=10
        )


def test_delete_address_wrong_user(
    billing_address_service,
    mock_repository
):
    address = create_address(
        user_id=20
    )

    mock_repository.get_by_id.return_value = (
        address
    )

    with pytest.raises(
        PermissionError,
        match=(
            "You do not have access to this "
            "billing address."
        )
    ):
        billing_address_service.delete_address(
            address_id=1,
            user_id=10
        )


def test_delete_address_rolls_back_on_error(
    billing_address_service,
    mock_repository,
    mock_session
):
    address = create_address()

    mock_repository.get_by_id.return_value = (
        address
    )

    mock_repository.delete.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        billing_address_service.delete_address(
            address_id=1,
            user_id=10
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()