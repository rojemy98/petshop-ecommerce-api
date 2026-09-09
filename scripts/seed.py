from decimal import Decimal
from random import randint, uniform

from faker import Faker
from werkzeug.security import generate_password_hash

from database.db_manager import DatabaseManager
from models import User, Product
from repositories import (
    UsersRepository,
    ProductsRepository,
)

from config import DATABASE_URL

fake = Faker()


def seed_users(
    users_repository: UsersRepository
) -> list[User]:

    users = []

    # Development admin
    admin = User(
        name="Admin",
        last_name="Petshop",
        email="admin@petshop.com",
        password_hash=generate_password_hash(
            "Admin123!"
        ),
        role="ADMIN"
    )

    users_repository.create(admin)
    users.append(admin)

    # Development client
    client = User(
        name="Test",
        last_name="Client",
        email="client@petshop.com",
        password_hash=generate_password_hash(
            "Client123!"
        ),
        role="CLIENT"
    )

    users_repository.create(client)
    users.append(client)

    # Random clients
    for _ in range(4):

        user = User(
            name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            password_hash=generate_password_hash(
                "Password123!"
            ),
            role="CLIENT"
        )

        users_repository.create(user)
        users.append(user)

    return users


def seed_products(
    products_repository: ProductsRepository,
    admin_id: int
) -> list[Product]:

    product_names = [
        "Premium Dog Food",
        "Premium Cat Food",
        "Dog Leash",
        "Dog Collar",
        "Cat Collar",
        "Cat Scratching Post",
        "Dog Bed",
        "Cat Bed",
        "Pet Shampoo",
        "Dog Toy Ball",
        "Cat Toy Mouse",
        "Pet Food Bowl",
        "Pet Water Bowl",
        "Dog Treats",
        "Cat Treats",
        "Pet Carrier",
        "Dog Brush",
        "Cat Brush",
        "Pet Blanket",
        "Training Pads",
    ]

    products = []

    for name in product_names:

        product = Product(
            name=name,
            price=Decimal(
                str(round(uniform(5, 100), 2))
            ),
            stock=randint(5, 100),
            created_by=admin_id
        )

        products_repository.create(product)
        products.append(product)

    return products


def main():

    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL environment variable is not configured."
        )

    db_manager = DatabaseManager(DATABASE_URL)

    session = db_manager.create_session()

    try:
        users_repository = UsersRepository(session)
        products_repository = ProductsRepository(session)

        users = seed_users(
            users_repository
        )

        admin = users[0]

        products = seed_products(
            products_repository,
            admin.id
        )

        session.commit()

        print("Database seeded successfully.")
        print(f"Users created: {len(users)}")
        print(f"Products created: {len(products)}")

        print("\nDevelopment credentials:")
        print("ADMIN")
        print("Email: admin@petshop.com")
        print("Password: Admin123!")

        print("\nCLIENT")
        print("Email: client@petshop.com")
        print("Password: Client123!")

    except Exception as error:
        session.rollback()

        print("Error seeding database:")
        print(error)

    finally:
        session.close()


if __name__ == "__main__":
    main()