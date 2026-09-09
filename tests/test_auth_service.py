from unittest.mock import Mock, patch

import pytest

from services.auth_service import AuthService


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_session():
    return Mock()


@pytest.fixture
def mock_jwt_manager():
    return Mock()


@pytest.fixture
def mock_users_repository():
    return Mock()


@pytest.fixture
def mock_login_history_repository():
    return Mock()


@pytest.fixture
def auth_service(
    mock_session,
    mock_jwt_manager,
    mock_users_repository,
    mock_login_history_repository
):
    service = AuthService(
        mock_session,
        mock_jwt_manager
    )

    service.users_repository = (
        mock_users_repository
    )

    service.login_history_repository = (
        mock_login_history_repository
    )

    return service


# ============================================================
# Helper
# ============================================================

def create_user(
    user_id=10,
    name="John",
    last_name="Doe",
    email="john@example.com",
    password_hash="hashed-password",
    role="CLIENT"
):
    user = Mock()

    user.id = user_id
    user.name = name
    user.last_name = last_name
    user.email = email
    user.password_hash = password_hash
    user.role = role

    return user


# ============================================================
# REGISTER
# ============================================================

@patch(
    "services.auth_service.generate_password_hash",
    return_value="hashed-password"
)
def test_register_success(
    mock_generate_password_hash,
    auth_service,
    mock_users_repository,
    mock_session,
    mock_jwt_manager
):
    mock_users_repository.get_by_email.return_value = (
        None
    )

    def assign_user_id(user):
        user.id = 10
        return user

    mock_users_repository.create.side_effect = (
        assign_user_id
    )

    mock_jwt_manager.encode.return_value = (
        "access-token"
    )

    result = auth_service.register(
        name="John",
        last_name="Doe",
        email="  JOHN@EXAMPLE.COM  ",
        password="password123"
    )

    assert result == "access-token"

    mock_users_repository.get_by_email.assert_called_once_with(
        "john@example.com"
    )

    mock_generate_password_hash.assert_called_once_with(
        "password123"
    )

    mock_users_repository.create.assert_called_once()

    created_user = (
        mock_users_repository
        .create
        .call_args[0][0]
    )

    assert created_user.name == "John"
    assert created_user.last_name == "Doe"
    assert created_user.email == "john@example.com"
    assert created_user.password_hash == "hashed-password"
    assert created_user.role == "CLIENT"

    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()

    mock_jwt_manager.encode.assert_called_once_with(
        {
            "id": 10,
            "role": "CLIENT"
        }
    )


def test_register_duplicate_email(
    auth_service,
    mock_users_repository,
    mock_session
):
    existing_user = create_user()

    mock_users_repository.get_by_email.return_value = (
        existing_user
    )

    with pytest.raises(
        ValueError,
        match="A user with this email already exists."
    ):
        auth_service.register(
            name="John",
            last_name="Doe",
            email=" JOHN@EXAMPLE.COM ",
            password="password123"
        )

    mock_users_repository.get_by_email.assert_called_once_with(
        "john@example.com"
    )

    mock_users_repository.create.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_not_called()


@patch(
    "services.auth_service.generate_password_hash",
    return_value="hashed-password"
)
def test_register_rolls_back_on_repository_error(
    mock_generate_password_hash,
    auth_service,
    mock_users_repository,
    mock_session
):
    mock_users_repository.get_by_email.return_value = (
        None
    )

    mock_users_repository.create.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        auth_service.register(
            name="John",
            last_name="Doe",
            email="john@example.com",
            password="password123"
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


# ============================================================
# LOGIN - USER NOT FOUND
# ============================================================

def test_login_user_not_found(
    auth_service,
    mock_users_repository,
    mock_login_history_repository,
    mock_session,
    mock_jwt_manager
):
    mock_users_repository.get_by_email.return_value = (
        None
    )

    with pytest.raises(
        ValueError,
        match="Invalid email or password."
    ):
        auth_service.login(
            email=" UNKNOWN@EXAMPLE.COM ",
            password="password123",
            ip_address="127.0.0.1"
        )

    mock_users_repository.get_by_email.assert_called_once_with(
        "unknown@example.com"
    )

    mock_login_history_repository.create.assert_called_once()

    login_history = (
        mock_login_history_repository
        .create
        .call_args[0][0]
    )

    assert login_history.user_id is None
    assert login_history.ip_address == "127.0.0.1"
    assert login_history.success is False

    mock_session.commit.assert_called_once_with()

    mock_jwt_manager.encode.assert_not_called()


# ============================================================
# LOGIN - INVALID PASSWORD
# ============================================================

@patch(
    "services.auth_service.check_password_hash",
    return_value=False
)
def test_login_invalid_password(
    mock_check_password_hash,
    auth_service,
    mock_users_repository,
    mock_login_history_repository,
    mock_session,
    mock_jwt_manager
):
    user = create_user(
        user_id=10,
        password_hash="hashed-password"
    )

    mock_users_repository.get_by_email.return_value = (
        user
    )

    with pytest.raises(
        ValueError,
        match="Invalid email or password."
    ):
        auth_service.login(
            email=" JOHN@EXAMPLE.COM ",
            password="wrong-password",
            ip_address="192.168.1.10"
        )

    mock_users_repository.get_by_email.assert_called_once_with(
        "john@example.com"
    )

    mock_check_password_hash.assert_called_once_with(
        "hashed-password",
        "wrong-password"
    )

    mock_login_history_repository.create.assert_called_once()

    login_history = (
        mock_login_history_repository
        .create
        .call_args[0][0]
    )

    assert login_history.user_id == 10
    assert login_history.ip_address == "192.168.1.10"
    assert login_history.success is False

    mock_session.commit.assert_called_once_with()

    mock_jwt_manager.encode.assert_not_called()


# ============================================================
# LOGIN - SUCCESS
# ============================================================

@patch(
    "services.auth_service.check_password_hash",
    return_value=True
)
def test_login_success(
    mock_check_password_hash,
    auth_service,
    mock_users_repository,
    mock_login_history_repository,
    mock_session,
    mock_jwt_manager
):
    user = create_user(
        user_id=10,
        password_hash="hashed-password",
        role="CLIENT"
    )

    mock_users_repository.get_by_email.return_value = (
        user
    )

    mock_jwt_manager.encode.return_value = (
        "access-token"
    )

    result = auth_service.login(
        email=" JOHN@EXAMPLE.COM ",
        password="password123",
        ip_address="127.0.0.1"
    )

    assert result == "access-token"

    mock_users_repository.get_by_email.assert_called_once_with(
        "john@example.com"
    )

    mock_check_password_hash.assert_called_once_with(
        "hashed-password",
        "password123"
    )

    mock_login_history_repository.create.assert_called_once()

    login_history = (
        mock_login_history_repository
        .create
        .call_args[0][0]
    )

    assert login_history.user_id == 10
    assert login_history.ip_address == "127.0.0.1"
    assert login_history.success is True

    mock_session.commit.assert_called_once_with()

    mock_jwt_manager.encode.assert_called_once_with(
        {
            "id": 10,
            "role": "CLIENT"
        }
    )


# ============================================================
# REGISTER LOGIN ATTEMPT
# ============================================================

def test_register_login_attempt_success(
    auth_service,
    mock_login_history_repository,
    mock_session
):
    result = auth_service._register_login_attempt(
        user_id=10,
        ip_address="127.0.0.1",
        success=True
    )

    assert result is None

    mock_login_history_repository.create.assert_called_once()

    login_history = (
        mock_login_history_repository
        .create
        .call_args[0][0]
    )

    assert login_history.user_id == 10
    assert login_history.ip_address == "127.0.0.1"
    assert login_history.success is True

    mock_session.commit.assert_called_once_with()
    mock_session.rollback.assert_not_called()


def test_register_login_attempt_anonymous_user(
    auth_service,
    mock_login_history_repository,
    mock_session
):
    auth_service._register_login_attempt(
        user_id=None,
        ip_address="10.0.0.1",
        success=False
    )

    login_history = (
        mock_login_history_repository
        .create
        .call_args[0][0]
    )

    assert login_history.user_id is None
    assert login_history.ip_address == "10.0.0.1"
    assert login_history.success is False

    mock_session.commit.assert_called_once_with()


def test_register_login_attempt_rolls_back_on_error(
    auth_service,
    mock_login_history_repository,
    mock_session
):
    mock_login_history_repository.create.side_effect = (
        Exception("Database error")
    )

    with pytest.raises(
        Exception,
        match="Database error"
    ):
        auth_service._register_login_attempt(
            user_id=10,
            ip_address="127.0.0.1",
            success=True
        )

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once_with()


# ============================================================
# GENERATE ACCESS TOKEN
# ============================================================

def test_generate_access_token(
    auth_service,
    mock_jwt_manager
):
    user = create_user(
        user_id=25,
        role="ADMIN"
    )

    mock_jwt_manager.encode.return_value = (
        "admin-token"
    )

    result = auth_service._generate_access_token(
        user
    )

    assert result == "admin-token"

    mock_jwt_manager.encode.assert_called_once_with(
        {
            "id": 25,
            "role": "ADMIN"
        }
    )