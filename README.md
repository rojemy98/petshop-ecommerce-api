# PetShop E-Commerce API

REST API developed with Python and Flask for managing a pet shop e-commerce platform.

The application provides authentication, role-based authorization, product management, shopping carts, checkout, billing addresses, invoices, payments, product returns, inventory management, Redis caching, and login history.

The project uses a layered architecture separating routes, services, repositories, and database models.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Database](#database)
- [Database ER Diagram](#database-er-diagram)
- [API Documentation](#api-documentation)
- [Installation](#installation)
- [Project Setup](#project-setup)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Roles](#roles)
- [Redis Cache](#redis-cache)
- [Transactions](#transactions)
- [Testing](#testing)
- [Automated Test Report](#automated-test-report)
- [Test Coverage](#test-coverage)
- [Security](#security)
- [Recommended .gitignore](#recommended-gitignore)
- [Author](#author)

---

## Features

### Authentication and Authorization

- User registration and login
- Password hashing
- JWT authentication using RS256
- Role-based authorization
- CLIENT and ADMIN roles
- Login attempt history
- Protected endpoints

### Product Management

Administrators can:

- Create products
- Update products
- Disable products
- Manage product stock

Clients can:

- View available products
- Add products to their shopping cart

### Shopping Cart

Clients can:

- Create or retrieve their active cart
- Add products
- Modify product quantities
- Remove products
- View previous carts
- Abandon carts
- Complete checkout

Product stock is validated when products are added to the cart and validated again during checkout.

Stock is only deducted when checkout is successfully completed.

### Billing Addresses

Clients can:

- Create billing addresses
- View their addresses
- Update addresses
- Delete addresses

Ownership validation prevents users from accessing billing addresses belonging to other users.

### Checkout

The checkout process:

1. Validates the cart and its ownership.
2. Validates that the cart is active and contains products.
3. Validates the selected billing address.
4. Validates product availability and stock.
5. Calculates the purchase total.
6. Creates an invoice.
7. Creates invoice product records.
8. Updates product stock.
9. Creates the payment record.
10. Marks the cart as completed.
11. Invalidates affected Redis cache entries.

The database operations are executed as a transaction.

### Invoices

Invoices contain:

- Unique invoice number
- User
- Billing address
- Products purchased
- Product quantities
- Purchase prices
- Total amount
- Payment information
- Purchase date
- Invoice status

Clients can access only their own invoices.

Administrators can access all invoices.

### Returns

The API supports product return requests.

Return statuses:

- `REQUESTED`
- `APPROVED`
- `REJECTED`
- `COMPLETED`

When a return is completed:

- Returned quantities are validated.
- Product stock is restored.
- Invoice return status is recalculated.
- Redis product cache is invalidated.

Invoice statuses include:

- `PAID`
- `PARTIALLY_REFUNDED`
- `REFUNDED`
- `CANCELLED`

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

Each layer has a specific responsibility.

**Routes**

Handle HTTP requests, authentication, authorization, request data, and HTTP responses.

**Services**

Contain business rules and coordinate operations between repositories.

**Repositories**

Handle database operations through SQLAlchemy.

**Models**

Represent database entities and relationships.

---

## Project Structure

```text
petshop-api/
│
├── app.py
├── .env
├── .gitignore
├── README.md
├── requirements.txt
│
├── auth/
│   └── decorators.py
│
├── cache/
│   └── cache_manager.py
│
├── config/
│   ├── settings.py
│   └── constants.py
│
├── database/
│   ├── db_manager.py
│   └── create_tables.py
│
├── keys/
│   ├── private.pem
│   └── public.pem
│
├── models/
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
│   ├── auth_routes.py
│   ├── product_routes.py
│   ├── cart_routes.py
│   ├── billing_address_routes.py
│   ├── invoice_routes.py
│   └── return_routes.py
│
├── services/
│   ├── auth_service.py
│   ├── jwt_manager.py
│   ├── product_service.py
│   ├── cart_service.py
│   ├── billing_address_service.py
│   ├── checkout_service.py
│   ├── invoice_service.py
│   └── return_service.py
│
├── scripts/
│   ├── seed.py
│   └── ...
│
└── tests/
    ├── test_auth_service.py
    ├── test_product_service.py
    ├── test_cart_service.py
    ├── test_billing_address_service.py
    ├── test_checkout_service.py
    ├── test_invoice_service.py
    └── test_return_service.py
```

---

## Technologies

The project uses:

- Python
- Flask
- PostgreSQL
- SQLAlchemy
- Redis
- PyJWT
- RSA / RS256
- Werkzeug
- pytest
- pytest-cov

---

## Database

The application uses PostgreSQL with SQLAlchemy ORM.

Database objects are stored inside the PostgreSQL schema:

```text
petshop_ecommerce
```

Main entities:

```text
User
LoginHistory
Product
Cart
CartProduct
BillingAddress
Invoice
InvoiceProduct
Payment
Return
ReturnProduct
```

SQLAlchemy relationships are used to represent associations between entities.

---

## Database ER Diagram

The following Entity-Relationship Diagram represents the PostgreSQL
database structure used by the application.

![PetShop E-Commerce Database ER Diagram](docs/database-diagram.jpg)

---

## API Documentation

Complete endpoint documentation, authentication requirements,
request bodies, and examples are available here:

[View API Documentation](docs/API.md)

---

## Installation

### 1. Clone the repository

```bash
git clone -b proyecto-final-flask https://github.com/rojemy98/DUAD_Lyfter.git
```

### 2. Navigate to the project directory

```bash
cd DUAD_Lyfter/06-flask/06-proyecto-final/petshop-api
```

### 3. Create and activate a virtual environment

#### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/postgres
REDIS_URL=redis://localhost:6379/0

CACHE_TTL=600

JWT_ALGORITHM=RS256
JWT_ACCESS_TOKEN_EXPIRES=900
```

Make sure PostgreSQL and Redis are available before starting the application.

> Do not commit the `.env` file to Git.

---

## Project Setup

After installing the dependencies and configuring the `.env` file, run the following setup steps from the `petshop-api` directory.

### 1. Generate RSA keys

The application uses RS256 for JWT authentication.

Run:

```bash
python -m scripts.generate_keys
```

This should generate:

```text
keys/
├── private.pem
└── public.pem
```

The private key is used to sign JWT tokens and the public key is used to verify them.

> Never commit `private.pem` to a public repository.

### 2. Create the database tables

Make sure the PostgreSQL database specified in `DATABASE_URL` already exists.

Then run:

```bash
python -m database.create_tables
```

This creates the required tables using SQLAlchemy ORM inside the PostgreSQL schema:

```text
petshop_ecommerce
```

No SQL scripts are required.

### 3. Seed the database

To populate the database with initial or test data, run:

```bash
python -m scripts.seed
```

This step is useful for creating sample users, products, invoices, or other initial data required for testing the API.

### 4. Configure Redis

The application uses Redis to cache product information.

Redis does not need to be hosted in the cloud. For local development, it can be executed locally using Docker.

Make sure Docker is installed and running, then create a Redis container:

```bash
docker run --name petshop-redis -p 6379:6379 -d redis
```

Verify that Redis is running:

```bash
docker exec -it petshop-redis redis-cli ping
```

The expected response is:

```text
PONG
```

Redis will now be available at:

```text
redis://localhost:6379/0
```

#### Managing the Redis container

If the container already exists but is stopped, start it with:

```bash
docker start petshop-redis
```

To stop it:

```bash
docker stop petshop-redis
```

You do not need to run `docker run` every time. That command creates the container. After it has been created, use `docker start` and `docker stop`.

---


### 5. Run the application

```bash
python app.py
```

The API will be available at:

```text
http://localhost:5000
```

---

## Quick Start

After configuring `.env`, the complete setup sequence is:

```bash
python -m scripts.generate_keys
python -m database.create_tables
python -m scripts.seed
python app.py
```

---

## Authentication

Protected endpoints require a JWT access token.

Send the token using:

```http
Authorization: Bearer <access_token>
```

Tokens contain the user's identifier and role.

Example payload:

```json
{
    "id": 1,
    "role": "CLIENT"
}
```

Access tokens expire automatically according to:

```env
JWT_ACCESS_TOKEN_EXPIRES=900
```

---

## Roles

### CLIENT

A client can perform operations such as:

- View products
- Manage their shopping cart
- Manage their billing addresses
- Complete purchases
- View their invoices
- Request product returns

### ADMIN

An administrator can perform administrative operations such as:

- Create products
- Update products
- Disable products
- View administrative resources
- Manage return statuses

---

## Redis Cache

Redis is used to reduce repeated database queries for product information.

Examples of cache keys:

```text
products:all
product:<product_id>
```

The default cache TTL is:

```text
600 seconds
```

or:

```text
10 minutes
```

### Why use a TTL?

Product information is frequently requested.

Caching this information:

- Reduces PostgreSQL queries.
- Improves response times.
- Reduces database workload.

The TTL guarantees that cached information eventually expires even if explicit invalidation does not occur.

### Cache Invalidation

Cache entries are invalidated when product information may change.

Examples include:

- Product creation
- Product update
- Product deletion/deactivation
- Checkout
- Completed returns

PostgreSQL remains the source of truth.

---

## Transactions

Operations that modify multiple database records use SQLAlchemy transactions.

For example, checkout can modify:

```text
Cart
Invoice
InvoiceProduct
Payment
Product stock
```

If an error occurs before the transaction is completed:

```python
session.rollback()
```

is used to prevent partially completed purchases.

Successful operations use:

```python
session.commit()
```

---

## Testing

Unit tests are implemented using `pytest`.

Run the complete test suite:

```bash
pytest -v
```

Run service coverage:

```bash
pytest --cov=services --cov-report=term-missing
```

Generate an HTML coverage report:

```bash
pytest --cov=services --cov-report=html
```

Then open:

```text
htmlcov/index.html
```

---

## Automated Test Report

The project includes a test runner that executes the complete unit test
suite and generates a coverage report.

```bash
python -m scripts.run_tests
```

---

## Test Coverage

Current service-layer coverage:

```text
Name                                  Cover
-------------------------------------------
services/auth_service.py               100%
services/billing_address_service.py    100%
services/cart_service.py                98%
services/checkout_service.py           100%
services/invoice_service.py            100%
services/jwt_manager.py                100%
services/product_service.py            100%
services/return_service.py             100%
-------------------------------------------
TOTAL                                   99%
```

The tests cover both successful operations and important failure scenarios such as:

- Invalid authentication
- Duplicate users
- Invalid product information
- Insufficient stock
- Invalid cart operations
- Unauthorized resource access
- Invalid billing addresses
- Checkout failures
- Invoice ownership
- Invalid return quantities
- Invalid return status transitions
- Transaction rollbacks

Repositories, database connections, Redis, and JWT dependencies are mocked where appropriate so unit tests remain isolated from external infrastructure.

---

## Security

The project implements several security practices:

- Password hashing
- JWT authentication
- RSA-based RS256 token signing
- Role-based authorization
- Resource ownership validation
- Login attempt history
- Environment variables for secrets
- Private key separation
- Input and business-rule validation

Sensitive files should never be committed to source control.

---

## Recommended `.gitignore`

```gitignore
# Environment variables
.env
.env.*

# Virtual environments
venv/
.venv/

# Python
__pycache__/
*.py[cod]
*$py.class

# Testing
.pytest_cache/
.coverage
.coverage.*
htmlcov/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# RSA private keys
keys/private.pem
*.key
```

The public key can normally be distributed because it cannot be used to sign tokens. The private key must remain secret.

---

## Author

**Rojemy Emanuel Diaz**

Computer Engineering
