
from decimal import Decimal
from random import randint

from faker import Faker
from werkzeug.security import generate_password_hash

from database.db_manager import DatabaseManager
from models import User, Product
from repositories import (
    UsersRepository,
    ProductsRepository,
)

from config import DATABASE_URL


fake = Faker("es_ES")


def seed_users(
    users_repository: UsersRepository
) -> list[User]:

    users = []

    # Development admin
    admin = User(
        name="Admin",
        last_name="Petshop",
        email="admin@petshop.com",
        password_hash=generate_password_hash("Admin123!"),
        role="ADMIN"
    )

    users_repository.create(admin)
    users.append(admin)

    # Development client
    client = User(
        name="Cliente",
        last_name="Prueba",
        email="client@petshop.com",
        password_hash=generate_password_hash("Client123!"),
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
            password_hash=generate_password_hash("Password123!"),
            role="CLIENT"
        )

        users_repository.create(user)
        users.append(user)

    return users


def seed_products(
    products_repository: ProductsRepository,
    admin_id: int
) -> list[Product]:

    product_data = [

        # ALIMENTOS
        {
            "name": "Alimento Premium para Perro Adulto",
            "category": "Alimentos",
            "price": 18500
        },
        {
            "name": "Alimento Premium para Cachorros",
            "category": "Alimentos",
            "price": 16200
        },
        {
            "name": "Alimento para Gato Adulto",
            "category": "Alimentos",
            "price": 14500
        },
        {
            "name": "Alimento para Gatitos",
            "category": "Alimentos",
            "price": 12800
        },
        {
            "name": "Snacks de Pollo para Perros",
            "category": "Alimentos",
            "price": 3200
        },
        {
            "name": "Galletas para Perros",
            "category": "Alimentos",
            "price": 2800
        },
        {
            "name": "Premios de Salmón para Gatos",
            "category": "Alimentos",
            "price": 3500
        },
        {
            "name": "Alimento Húmedo para Gatos",
            "category": "Alimentos",
            "price": 1800
        },
        {
            "name": "Alimento Húmedo para Perros",
            "category": "Alimentos",
            "price": 2200
        },
        {
            "name": "Huesos Masticables para Perros",
            "category": "Alimentos",
            "price": 4500
        },

        # ACCESORIOS
        {
            "name": "Collar Ajustable para Perro",
            "category": "Accesorios",
            "price": 5500
        },
        {
            "name": "Correa de Paseo para Perro",
            "category": "Accesorios",
            "price": 6500
        },
        {
            "name": "Arnés Acolchado para Perro",
            "category": "Accesorios",
            "price": 9500
        },
        {
            "name": "Collar para Gato con Cascabel",
            "category": "Accesorios",
            "price": 3500
        },
        {
            "name": "Plato de Acero Inoxidable",
            "category": "Accesorios",
            "price": 4200
        },
        {
            "name": "Dispensador de Agua para Mascotas",
            "category": "Accesorios",
            "price": 12500
        },
        {
            "name": "Transportadora para Gatos",
            "category": "Accesorios",
            "price": 18500
        },
        {
            "name": "Mochila Transportadora para Mascotas",
            "category": "Accesorios",
            "price": 24500
        },
        {
            "name": "Identificador para Collar",
            "category": "Accesorios",
            "price": 2500
        },
        {
            "name": "Botella Portátil para Paseos",
            "category": "Accesorios",
            "price": 4800
        },

        # HIGIENE
        {
            "name": "Champú para Perros",
            "category": "Higiene",
            "price": 5200
        },
        {
            "name": "Champú para Gatos",
            "category": "Higiene",
            "price": 4800
        },
        {
            "name": "Cepillo para Pelo de Perro",
            "category": "Higiene",
            "price": 3900
        },
        {
            "name": "Cepillo para Pelo de Gato",
            "category": "Higiene",
            "price": 3500
        },
        {
            "name": "Cortaúñas para Mascotas",
            "category": "Higiene",
            "price": 4200
        },
        {
            "name": "Toallitas Húmedas para Mascotas",
            "category": "Higiene",
            "price": 2800
        },
        {
            "name": "Arena Sanitaria para Gatos",
            "category": "Higiene",
            "price": 6500
        },
        {
            "name": "Alfombras Absorbentes para Perros",
            "category": "Higiene",
            "price": 7500
        },
        {
            "name": "Limpiador de Oídos para Mascotas",
            "category": "Higiene",
            "price": 4500
        },
        {
            "name": "Guantes para Cepillado",
            "category": "Higiene",
            "price": 3200
        },

        # CAMAS Y DESCANSO
        {
            "name": "Cama Acolchada para Perro Pequeño",
            "category": "Camas y descanso",
            "price": 14500
        },
        {
            "name": "Cama Acolchada para Perro Grande",
            "category": "Camas y descanso",
            "price": 22500
        },
        {
            "name": "Cama Redonda para Gatos",
            "category": "Camas y descanso",
            "price": 12500
        },
        {
            "name": "Manta Suave para Mascotas",
            "category": "Camas y descanso",
            "price": 6500
        },
        {
            "name": "Almohada para Perros",
            "category": "Camas y descanso",
            "price": 8500
        },
        {
            "name": "Casa de Tela para Gatos",
            "category": "Camas y descanso",
            "price": 16500
        },
        {
            "name": "Colchón Ortopédico para Perros",
            "category": "Camas y descanso",
            "price": 28500
        },
        {
            "name": "Hamaca para Gatos",
            "category": "Camas y descanso",
            "price": 11500
        },
        {
            "name": "Cojín Reversible para Mascotas",
            "category": "Camas y descanso",
            "price": 9500
        },
        {
            "name": "Manta Térmica para Mascotas",
            "category": "Camas y descanso",
            "price": 13500
        },

        # JUGUETES
        {
            "name": "Pelota de Goma para Perros",
            "category": "Juguetes",
            "price": 2800
        },
        {
            "name": "Pelota Interactiva para Gatos",
            "category": "Juguetes",
            "price": 3500
        },
        {
            "name": "Ratón de Juguete para Gatos",
            "category": "Juguetes",
            "price": 1800
        },
        {
            "name": "Cuerda para Morder",
            "category": "Juguetes",
            "price": 3200
        },
        {
            "name": "Rascador para Gatos",
            "category": "Juguetes",
            "price": 18500
        },
        {
            "name": "Juguete Dispensador de Premios",
            "category": "Juguetes",
            "price": 7500
        },
        {
            "name": "Túnel de Juego para Gatos",
            "category": "Juguetes",
            "price": 9500
        },
        {
            "name": "Peluches para Perros",
            "category": "Juguetes",
            "price": 4200
        },
        {
            "name": "Varita Interactiva para Gatos",
            "category": "Juguetes",
            "price": 2500
        },
        {
            "name": "Frisbee para Perros",
            "category": "Juguetes",
            "price": 3800
        },
    ]

    products = []

    for item in product_data:
        product = Product(
            name=item["name"],
            category=item["category"],
            price=Decimal(str(item["price"])),
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

        users = seed_users(users_repository)
        admin = users[0]

        products = seed_products(
            products_repository,
            admin.id
        )

        session.commit()

        print("\nDatabase seeded successfully.")
        print(f"Users created: {len(users)}")
        print(f"Products created: {len(products)}")

        print("\nProducts by category:")

        categories = {}

        for product in products:
            categories[product.category] = (
                categories.get(product.category, 0) + 1
            )

        for category, total in categories.items():
            print(f"- {category}: {total}")

        print("\nDevelopment credentials:")
        print("ADMIN")
        print("Email: admin@petshop.com")
        print("Password: Admin123!")

        print("\nCLIENT")
        print("Email: client@petshop.com")
        print("Password: Client123!")

    except Exception as error:
        session.rollback()

        print("\nError seeding database:")
        print(error)

        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()
