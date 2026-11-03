# PetShop E-Commerce API

A RESTful API built with Python and Flask for managing an e-commerce platform for pet products.

The application provides user authentication, role-based authorization, product and inventory management, shopping carts, checkout, billing addresses, invoices, payments, product returns, login history, and Redis caching.

The backend follows a layered architecture that separates HTTP routes, business logic, database operations, and data models.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Database](#database)
- [API Documentation](#api-documentation)
- [Installation](#installation)
- [Configuration](#configuration)
- [Project Setup](#project-setup)
- [Running the Application](#running-the-application)
- [Authentication and Authorization](#authentication-and-authorization)
- [Redis Caching](#redis-caching)
- [Transactions](#transactions)
- [Database Seeding](#database-seeding)
- [Testing](#testing)
- [Security](#security)
- [Author](#author)

---

## Features

### Authentication and User Management

- User registration and login.
- Password hashing.
- JWT authentication using RSA and RS256.
- Role-based access control.
- CLIENT and ADMIN roles.
- Login attempt history.
- User profile management.
- Password changes.
- Administrative user management.
- Session revocation for administrative operations.

### Product and Inventory Management

Administrators can:

- Create products.
- Update product information.
- Update prices and stock.
- Deactivate products through soft deletion.
- View the complete product inventory.

Clients can:

- Browse available products.
- View product details.
- Access products available in the store.

Products include information such as name, category, price, stock, active status, and audit information.

### Shopping Cart

Authenticated users can:

- Create a shopping cart.
- Retrieve their active cart.
- View their previous carts.
- Add products.
- Update product quantities.
- Remove products.
- Abandon an active cart.
- Complete checkout.

Each user can have only one active cart at a time.

The API validates product availability and stock when products are added or quantities are updated. Stock is deducted only after a successful checkout.

**Important:** `GET /carts/active` only retrieves an existing active cart. It does not create one. Use `POST /carts` to create a cart.

### Checkout and Payments

The checkout process:

1. Validates cart ownership and status.
2. Checks that the cart contains products.
3. Validates the selected billing address.
4. Validates product availability and stock.
5. Calculates the purchase total.
6. Creates an invoice.
7. Creates invoice product records.
8. Updates product stock.
9. Creates a payment record.
10. Marks the cart as completed.
11. Invalidates affected Redis cache entries.

The checkout operation uses database transactions to maintain data consistency.

### Billing Addresses

Authenticated users can:

- Create billing addresses.
- Retrieve their addresses.
- Update addresses.
- Delete addresses.

Ownership validation prevents users from accessing addresses belonging to other users.

### Invoices

Invoices are generated through the checkout process and contain purchase information, including:

- Invoice number.
- Customer information.
- Billing address.
- Purchased products and quantities.
- Purchase prices.
- Total amount.
- Payment information.
- Invoice status.

Clients can access only their own invoices. Administrators can access invoices across the system.

### Product Returns

The API supports return requests associated with existing invoices.

Supported return statuses:

- `REQUESTED`
- `APPROVED`
- `REJECTED`
- `COMPLETED`

When a return is completed:

- Returned quantities are validated.
- Product stock is restored.
- Invoice return status is recalculated.
- Relevant product cache entries are invalidated.

The service also validates previously completed return quantities to prevent returning more units than originally purchased.

---

## Architecture

The project follows a layered architecture:

```text
             HTTP Request
                  |
                  v
                Routes
                  |
                  v
               Services
                  |
                  v
             Repositories
                  |
                  v
              SQLAlchemy
                  |
                  v
              PostgreSQL
```

**Routes**

Handle HTTP requests, authentication, authorization, request validation, and HTTP responses.

**Services**

Contain business rules and coordinate application operations.

**Repositories**

Encapsulate database queries and persistence operations using SQLAlchemy.

**Models**

Represent database entities, attributes, and relationships.

**Infrastructure**

Redis provides caching, while the database manager handles SQLAlchemy sessions and database connections.

---

## Project Structure

```text
petshop-ecommerce-api/
│
├── auth/
│   └── decorators.py
│
├── cache/
│   └── cache_manager.py
│
├── config/
│   ├── __init__.py
│   ├── constants.py
│   └── settings.py
│
├── database/
│   ├── __init__.py
│   └── db_manager.py
│
├── docs/
│   ├── API.md
│   └── database-diagram.jpg
│
├── keys/
│   ├── private.pem
│   └── public.pem
│
├── models/
│   ├── __init__.py
│   ├── base.py
│   ├── user.py
│   ├── product.py
│   ├── cart.py
│   ├── cart_product.py
│   ├── billing_address.py
│   ├── invoice.py
│   ├── invoice_product.py
│   ├── payment.py
│   ├── login_history.py
│   ├── return_model.py
│   └── return_product.py
│
├── repositories/
│   ├── __init__.py
│   ├── base_repository.py
│   ├── users_repository.py
│   ├── products_repository.py
│   ├── carts_repository.py
│   ├── billing_addresses_repository.py
│   ├── invoices_repository.py
│   ├── invoice_products_repository.py
│   ├── payments_repository.py
│   ├── login_history_repository.py
│   ├── returns_repository.py
│   └── return_products_repository.py
│
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── product_routes.py
│   ├── cart_routes.py
│   ├── billing_address_routes.py
│   ├── invoice_routes.py
│   ├── return_routes.py
│   └── user_routes.py
│
├── scripts/
│   ├── create_tables.py
│   ├── generate_keys.py
│   ├── run_tests.py
│   ├── seed.py
│   ├── test_cache.py
│   └── test_jwt_manager.py
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── billing_address_service.py
│   ├── cart_service.py
│   ├── checkout_service.py
│   ├── invoice_service.py
│   ├── jwt_manager.py
│   ├── product_service.py
│   ├── return_service.py
│   └── user_service.py
│
├── tests/
│   ├── test_auth_service.py
│   ├── test_product_service.py
│   ├── test_cart_service.py
│   ├── test_billing_address_service.py
│   ├── test_checkout_service.py
│   ├── test_invoice_service.py
│   └── test_return_service.py
│
├── app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

_The RSA key files are generated locally and should not be committed with private key contents._

---

## Technologies

| Technology    | Purpose                         |
| ------------- | ------------------------------- |
| Python        | Backend programming language    |
| Flask         | REST API framework              |
| PostgreSQL    | Relational database             |
| SQLAlchemy    | ORM and database operations     |
| Redis         | Product data caching            |
| PyJWT         | JWT authentication              |
| RS256 / RSA   | Asymmetric token signing        |
| Werkzeug      | Password hashing utilities      |
| Flask-Cors    | Cross-origin resource sharing   |
| pytest        | Automated testing               |
| pytest-cov    | Test coverage reporting         |
| Faker         | Test data generation            |
| python-dotenv | Environment variable management |

---

## Database

The application uses PostgreSQL with SQLAlchemy ORM.

Database objects are organized under the following schema:

```text
petshop_ecommerce
```

Main entities:

- User
- LoginHistory
- Product
- Cart
- CartProduct
- BillingAddress
- Invoice
- InvoiceProduct
- Payment
- Return
- ReturnProduct

SQLAlchemy models define the relationships between entities.

### Database ER Diagram

The database entity-relationship diagram is available here:

![PetShop E-Commerce Database ER Diagram](docs/database-diagram.jpg)

---

## API Documentation

Detailed API documentation is available in:

[View API Documentation](docs/API.md)

The documentation includes:

- Endpoint descriptions.
- HTTP methods and URL paths.
- Authentication requirements.
- User role permissions.
- Request body examples.
- Response examples.
- HTTP status codes.
- Validation rules.

### Main Endpoint Groups

| Resource          | Base path            | Description                       |
| ----------------- | -------------------- | --------------------------------- |
| Authentication    | `/auth`              | Registration, login, current user |
| Users             | `/users`             | User and profile management       |
| Products          | `/products`          | Product catalog and inventory     |
| Carts             | `/carts`             | Shopping cart and checkout        |
| Billing Addresses | `/billing-addresses` | Billing address management        |
| Invoices          | `/invoices`          | Invoice retrieval                 |
| Returns           | `/returns`           | Product return management         |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/rojemy98/petshop-ecommerce-api.git
```

### 2. Navigate to the project directory

```bash
cd petshop-ecommerce-api
```

### 3. Create a virtual environment

**Windows**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

The project also requires `Flask-Cors`, which must be included in `requirements.txt` because the application imports it in `app.py`.

If it is not already listed, install it with:

```bash
pip install Flask-Cors
```

For reproducible installations, add the installed version to `requirements.txt`.

---

## Configuration

Create a `.env` file in the project root using `.env.example` as a reference.

Example:

```env
# PostgreSQL
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/postgres

# Redis
REDIS_URL=redis://localhost:6379/0

# Cache expiration in seconds
CACHE_TTL=600

# JWT
JWT_ALGORITHM=RS256
JWT_ACCESS_TOKEN_EXPIRES=900
```

### Environment Variables

| Variable                   | Description                      | Example                                                      |
| -------------------------- | -------------------------------- | ------------------------------------------------------------ |
| `DATABASE_URL`             | PostgreSQL connection string     | `postgresql+psycopg://user:password@localhost:5432/postgres` |
| `REDIS_URL`                | Redis connection URL             | `redis://localhost:6379/0`                                   |
| `CACHE_TTL`                | Cache expiration time in seconds | `600`                                                        |
| `JWT_ALGORITHM`            | JWT signing algorithm            | `RS256`                                                      |
| `JWT_ACCESS_TOKEN_EXPIRES` | Access token lifetime in seconds | `900`                                                        |

The application requires both `DATABASE_URL` and `REDIS_URL`.

The default JWT algorithm is RS256, and the default access token lifetime is 900 seconds (15 minutes).

**Important:** Never commit your actual `.env` file or private RSA key to source control.

---

## Project Setup

Complete the following steps before running the application.

### 1. Start PostgreSQL

Make sure PostgreSQL is installed and running.

Create the database specified in `DATABASE_URL` if it does not already exist.

The application creates its tables inside the `petshop_ecommerce` schema.

### 2. Generate RSA Keys

The application uses RS256 for JWT authentication.

Run:

```bash
python -m scripts.generate_keys
```

This generates the following files:

```text
keys/
├── private.pem
└── public.pem
```

The private key signs JWT tokens. The public key verifies them.

Do not share or commit the private key.

### 3. Create Database Tables

Run the following command from the project root:

```bash
python -m scripts.create_tables
```

This creates the database schema and tables using SQLAlchemy.

The PostgreSQL database itself must already exist.

### 4. Start Redis

Redis is used to cache product information.

For local development, Redis can be run using Docker.

Create and start a Redis container:

```bash
docker run --name petshop-redis -p 6379:6379 -d redis
```

Verify that Redis is running:

```bash
docker exec -it petshop-redis redis-cli ping
```

Expected response:

```text
PONG
```

Redis will be available at:

```text
redis://localhost:6379/0
```

#### Managing the Redis Container

Start an existing container:

```bash
docker start petshop-redis
```

Stop the container:

```bash
docker stop petshop-redis
```

The `docker run` command is only needed when creating the container for the first time.

---

## Running the Application

After configuring the environment and starting PostgreSQL and Redis, run:

```bash
python app.py
```

The API will be available at:

```text
http://localhost:5000
```

The application uses Flask's development server. For production deployments, use an appropriate production WSGI server and deployment configuration.

---

## Authentication and Authorization

The API uses JWT access tokens signed with RSA and RS256.

Protected endpoints require the following HTTP header:

```http
Authorization: Bearer <access_token>
```

### Authentication Endpoints

| Method | Endpoint         | Description                             |
| ------ | ---------------- | --------------------------------------- |
| POST   | `/auth/register` | Register a CLIENT account               |
| POST   | `/auth/login`    | Authenticate a user                     |
| GET    | `/auth/me`       | Retrieve authenticated user information |

### User Roles

**CLIENT**

Clients can:

- Browse available products.
- Manage their own shopping carts.
- Manage their own billing addresses.
- Complete purchases.
- View their own invoices.
- Request product returns.
- Manage their own profile and password.

**ADMIN**

Administrators can:

- Manage products and inventory.
- View administrative product listings.
- Manage users.
- Access administrative resources.
- View invoices across the system.
- Manage return request statuses.
- Revoke user sessions.

Authorization and resource ownership are validated by the backend.

---

## Redis Caching

Redis reduces repeated PostgreSQL queries for frequently requested product information.

### Cache Keys

The application uses the following product cache keys:

| Key                    | Purpose                                     |
| ---------------------- | ------------------------------------------- |
| `products:available`   | Available products for the storefront       |
| `products:admin:all`   | Complete product listing for administrators |
| `product:<product_id>` | Individual product information              |

### Cache TTL

The default cache expiration time is:

```text
600 seconds
```

Equivalent to:

```text
10 minutes
```

The value can be changed through the `CACHE_TTL` environment variable.

### Cache Invalidation

Relevant cache entries are invalidated when product information changes.

Examples include:

- Product creation.
- Product updates.
- Product deactivation.
- Checkout operations.
- Completed product returns.

PostgreSQL remains the source of truth.

---

## Transactions

Operations that modify multiple database records use SQLAlchemy transactions.

For example, checkout can affect:

```text
Cart
Invoice
InvoiceProduct
Payment
Product stock
```

Transactions help ensure that related database changes are completed consistently.

If an operation fails, the transaction is rolled back to prevent partially completed operations.

Successful operations are committed to the database.

---

## Database Seeding

The project includes a seed script to populate the database with development data.

Run:

```bash
python -m scripts.seed
```

The script creates sample users and products.

The current seed includes:

- An ADMIN user.
- A CLIENT user.
- Additional sample CLIENT users.
- 50 sample products distributed across five categories.

### Development Credentials

The seed script provides the following development accounts:

**ADMIN**

```text
Email: admin@petshop.com
Password: Admin123!
```

**CLIENT**

```text
Email: client@petshop.com
Password: Client123!
```

These credentials are intended exclusively for local development and testing. Do not use them in production.

---

## Testing

The project uses `pytest` for automated unit testing and `pytest-cov` for coverage reporting.

### Run the Test Suite

```bash
pytest -v
```

### Run Tests with Coverage

```bash
pytest --cov=services --cov-report=term-missing
```

### Generate an HTML Coverage Report

```bash
pytest --cov=services --cov-report=html
```

The generated report can be opened at:

```text
htmlcov/index.html
```

### Automated Test Runner

The repository also includes a script that executes the test suite and generates a service-layer coverage report.

Run:

```bash
python -m scripts.run_tests
```

The script returns a non-zero exit code if the tests fail.

### Test Scenarios

The test suite covers important application scenarios, including:

- Authentication and invalid credentials.
- Duplicate user registration.
- Product validation.
- Insufficient product stock.
- Shopping cart operations.
- Billing address ownership.
- Checkout operations and failures.
- Invoice ownership.
- Product return validation.
- Invalid return status transitions.
- Transaction rollback behavior.

Coverage results should be generated from the current codebase rather than treated as a fixed project value.

---

## Security

The application implements several security practices:

- Password hashing.
- JWT authentication.
- RSA-based RS256 token signing.
- Role-based authorization.
- Resource ownership validation.
- Login attempt history.
- Environment-based configuration.
- Input validation and business-rule validation.
- Separation of private and public RSA keys.

### Security Considerations

- Never commit `.env` files containing real credentials.
- Never expose the RSA private key.
- Use strong database credentials.
- Do not use development seed credentials in production.
- Configure production CORS origins explicitly.
- Use a production WSGI server instead of Flask's development server.
- Keep dependencies updated.

---

## Author

**Rojemy Emanuel Diaz**

GitHub: [rojemy98](https://github.com/rojemy98)

Repository: [petshop-ecommerce-api](https://github.com/rojemy98/petshop-ecommerce-api)
