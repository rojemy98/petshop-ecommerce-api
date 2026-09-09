from .auth_routes import create_auth_blueprint
from .product_routes import create_products_blueprint
from .cart_routes import create_carts_blueprint
from .billing_address_routes import create_billing_addresses_blueprint
from .invoice_routes import create_invoices_blueprint
from .return_routes import create_returns_blueprint
from .user_routes import create_user_blueprint


__all__ = [
    "create_auth_blueprint",
    "create_products_blueprint",
    "create_carts_blueprint",
    "create_billing_addresses_blueprint",
    "create_invoices_blueprint",
    "create_returns_blueprint",
    "create_user_blueprint",
]