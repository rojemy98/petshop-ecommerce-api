from flask import Flask

from config import (
    DATABASE_URL,
    REDIS_URL,
    CACHE_TTL,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES,
    load_private_key,
    load_public_key,
)

from database import DatabaseManager
from cache import CacheManager
from services import JWTManager

from routes import (
    create_auth_blueprint,
    create_products_blueprint,
    create_carts_blueprint,
    create_billing_addresses_blueprint,
    create_invoices_blueprint,
    create_returns_blueprint,
    create_user_blueprint,
)


def create_app():
    app = Flask(__name__)

    db_manager = DatabaseManager(DATABASE_URL)

    jwt_manager = JWTManager(
        private_key=load_private_key(),
        public_key=load_public_key(),
        algorithm=JWT_ALGORITHM,
        access_token_expires=JWT_ACCESS_TOKEN_EXPIRES
    )

    cache_manager = CacheManager(REDIS_URL)

    auth_blueprint = create_auth_blueprint(
        db_manager,
        jwt_manager
    )

    products_blueprint = create_products_blueprint(
        db_manager,
        jwt_manager,
        cache_manager
    )

    carts_blueprint = create_carts_blueprint(
        db_manager,
        jwt_manager,
        cache_manager
    )

    billing_addresses_blueprint = create_billing_addresses_blueprint(
        db_manager,
        jwt_manager
    )

    invoices_blueprint = create_invoices_blueprint(
        db_manager,
        jwt_manager
    )

    returns_blueprint = create_returns_blueprint(
        db_manager,
        jwt_manager,
        cache_manager
    )

    users_blueprint = create_user_blueprint(
        db_manager,
        jwt_manager,
    )

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(products_blueprint)
    app.register_blueprint(carts_blueprint)
    app.register_blueprint(billing_addresses_blueprint)
    app.register_blueprint(invoices_blueprint)
    app.register_blueprint(returns_blueprint)
    app.register_blueprint(users_blueprint)

    return app


app = create_app()
app.json.sort_keys = False


if __name__ == "__main__":
    app.run(debug=True)