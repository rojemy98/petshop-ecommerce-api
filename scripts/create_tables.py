from database.db_manager import DatabaseManager

from config import DATABASE_URL

from models import (
    User,
    LoginHistory,
    Product,
    Cart,
    CartProduct,
    BillingAddress,
    Invoice,
    InvoiceProduct,
    Payment,
    Return,
    ReturnProduct,
)


if __name__ == "__main__":

    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL environment variable is not configured."
        )

    db_manager = DatabaseManager(DATABASE_URL)

    try:
        db_manager.create_tables()

        print(
            "Database schema and tables "
            "created successfully."
        )

    finally:
        db_manager.close()