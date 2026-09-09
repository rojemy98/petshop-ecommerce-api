# PetShop E-Commerce API Documentation

## Base URL

```text
http://localhost:5000
```

The PetShop E-Commerce API provides authentication, user management, product management, shopping carts, billing addresses, checkout, invoices, and product returns.

The API uses JWT authentication with the RS256 algorithm.

Protected endpoints require the following header:

```http
Authorization: Bearer <access_token>
```

---

# Authentication

## Register User

```http
POST /auth/register
```

Creates a new user with the `CLIENT` role.

### Request

```json
{
  "name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "Password123!"
}
```

### Success Response

```http
201 Created
```

```json
{
  "id": 2,
  "name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "role": "CLIENT"
}
```

### Possible Errors

- `400 Bad Request` — Missing or invalid data.
- `409 Conflict` — Email already registered.

---

## Login

```http
POST /auth/login
```

Authenticates a user and returns a JWT access token.

### Request

```json
{
  "email": "john@example.com",
  "password": "Password123!"
}
```

### Success Response

```http
200 OK
```

```json
{
  "access_token": "<jwt_token>"
}
```

### Possible Errors

- `400 Bad Request` — Missing required fields.
- `401 Unauthorized` — Invalid email or password.

---

## Get Current User

```http
GET /auth/me
```

Returns information about the authenticated user.

### Authentication

Required.

### Success Response

```http
200 OK
```

```json
{
  "id": 2,
  "name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "role": "CLIENT"
}
```

### Possible Errors

- `401 Unauthorized` — Missing, expired, or invalid token.

---

# Users

User management endpoints are restricted to administrators.

## Get All Users

```http
GET /users
```

Returns all registered users.

### Role

`ADMIN`

### Success Response

```http
200 OK
```

```json
[
  {
    "id": 1,
    "name": "Admin",
    "last_name": "User",
    "email": "admin@petshop.com",
    "role": "ADMIN"
  },
  {
    "id": 2,
    "name": "Client",
    "last_name": "User",
    "email": "client@petshop.com",
    "role": "CLIENT"
  }
]
```

If there are no users:

```json
[]
```

### Possible Errors

- `401 Unauthorized`
- `403 Forbidden`

---

## Get User by ID

```http
GET /users/<user_id>
```

Returns a specific user.

### Role

`ADMIN`

### Success Response

```http
200 OK
```

```json
{
  "id": 2,
  "name": "Client",
  "last_name": "User",
  "email": "client@petshop.com",
  "role": "CLIENT"
}
```

### Possible Errors

- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found` — User does not exist.

---

## Create User

```http
POST /users
```

Allows an administrator to create a user.

Unlike `/auth/register`, this endpoint can assign a role.

### Role

`ADMIN`

### Request

```json
{
  "name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "password": "Password123!",
  "role": "CLIENT"
}
```

The `role` field is optional and defaults to:

```text
CLIENT
```

Supported roles:

```text
CLIENT
ADMIN
```

### Success Response

```http
201 Created
```

### Possible Errors

- `400 Bad Request` — Invalid or missing data.
- `401 Unauthorized`
- `403 Forbidden`
- `409 Conflict` — Email already registered, if handled as a conflict.

---

## Update User

```http
PUT /users/<user_id>
```

Updates an existing user.

### Role

`ADMIN`

### Request Example

```json
{
  "name": "Jane Updated",
  "role": "ADMIN"
}
```

Only provided fields are updated.

### Success Response

```http
200 OK
```

### Possible Errors

- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

## Delete User

```http
DELETE /users/<user_id>
```

Deletes a user.

### Role

`ADMIN`

### Success Response

```http
204 No Content
```

### Possible Errors

- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

# Products

## Get All Available Products

```http
GET /products
```

Returns all active products available in the store.

Inactive or soft-deleted products are excluded.

### Success Response

```http
200 OK
```

```json
[
  {
    "id": 1,
    "name": "Dog Food",
    "price": 15000,
    "stock": 20,
    "is_active": true
  }
]
```

If no products are available:

```json
[]
```

This endpoint may use Redis cache.

---

## Get Product by ID

```http
GET /products/<product_id>
```

Returns a specific active product.

### Success Response

```http
200 OK
```

### Possible Errors

- `404 Not Found`

---

## Create Product

```http
POST /products
```

Creates a new product.

### Role

`ADMIN`

### Request

```json
{
  "name": "Cat Food",
  "price": 12000,
  "stock": 30
}
```

### Success Response

```http
201 Created
```

### Possible Errors

- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `409 Conflict` — Duplicate product name, if handled as a conflict.

---

## Update Product

```http
PUT /products/<product_id>
```

Updates an existing product.

### Role

`ADMIN`

### Request Example

```json
{
  "price": 13500,
  "stock": 40
}
```

### Success Response

```http
200 OK
```

### Possible Errors

- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

## Delete Product

```http
DELETE /products/<product_id>
```

Soft-deletes a product by setting it as inactive.

### Role

`ADMIN`

### Success Response

```http
204 No Content
```

### Possible Errors

- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

# Carts

Cart endpoints operate on the currently authenticated user.

A user can only have one `ACTIVE` cart at a time.

---

## Get User Carts

```http
GET /carts
```

Returns all carts belonging to the authenticated user.

### Authentication

Required.

### Success Response

```http
200 OK
```

```json
[
  {
    "id": 1,
    "user_id": 2,
    "status": "COMPLETED"
  },
  {
    "id": 4,
    "user_id": 2,
    "status": "ACTIVE"
  }
]
```

If the user does not have carts:

```http
200 OK
```

```json
[]
```

---

## Create Active Cart

```http
POST /carts
```

Creates a new `ACTIVE` cart for the authenticated user.

This endpoint is responsible for creating carts.

A user cannot create another cart while an `ACTIVE` cart already exists.

### Authentication

Required.

### Success Response

```http
201 Created
```

```json
{
  "id": 5,
  "user_id": 2,
  "status": "ACTIVE",
  "cart_products": []
}
```

### Active Cart Already Exists

```http
409 Conflict
```

```json
{
  "message": "User already has an active cart."
}
```

### Possible Errors

- `401 Unauthorized`
- `409 Conflict` — User already has an active cart.

---

## Get Active Cart

```http
GET /carts/active
```

Returns the authenticated user's current active cart.

**This endpoint does not create a cart.**

If an active cart does not exist, the API returns `404 Not Found`.

### Authentication

Required.

### Success Response

```http
200 OK
```

```json
{
  "id": 5,
  "user_id": 2,
  "status": "ACTIVE",
  "cart_products": []
}
```

### No Active Cart

```http
404 Not Found
```

```json
{
  "message": "User does not have an active cart."
}
```

---

## Get Cart by ID

```http
GET /carts/<cart_id>
```

Returns a specific cart belonging to the authenticated user.

### Success Response

```http
200 OK
```

### Possible Errors

- `401 Unauthorized`
- `403 Forbidden` — Cart belongs to another user.
- `404 Not Found` — Cart does not exist.

---

## Add Product to Cart

```http
POST /carts/<cart_id>/items
```

Adds a product to an active cart.

### Request

```json
{
  "product_id": 3,
  "quantity": 2
}
```

`product_id` must be a positive integer.

`quantity` must be a positive integer.

### Success Response

```http
201 Created
```

### Possible Errors

- `400 Bad Request` — Invalid product ID or quantity.
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found` — Cart or product not found.
- `409 Conflict` — Operation conflicts with the current cart state, if applicable.

---

## Update Product Quantity

```http
PUT /carts/<cart_id>/items/<product_id>
```

Updates the quantity of a product already present in the cart.

### Request

```json
{
  "quantity": 4
}
```

### Success Response

```http
200 OK
```

### Possible Errors

- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

## Remove Product from Cart

```http
DELETE /carts/<cart_id>/items/<product_id>
```

Removes a product from a cart.

### Success Response

```http
204 No Content
```

### Possible Errors

- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

## Delete Cart

```http
DELETE /carts/<cart_id>
```

Deletes the specified cart if the authenticated user has permission to modify it.

### Success Response

```http
204 No Content
```

### Possible Errors

- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

# Billing Addresses

Billing address endpoints operate on addresses belonging to the authenticated user.

## Get Billing Addresses

```http
GET /billing-addresses
```

Returns the authenticated user's billing addresses.

### Success Response

```http
200 OK
```

If no addresses exist:

```json
[]
```

---

## Get Billing Address by ID

```http
GET /billing-addresses/<address_id>
```

### Success Response

```http
200 OK
```

### Possible Errors

- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

## Create Billing Address

```http
POST /billing-addresses
```

### Request Example

```json
{
  "address": "San Rafael",
  "city": "Heredia",
  "province": "Heredia",
  "postal_code": 40501,
  "country": "Costa Rica"
}
```

### Success Response

```http
201 Created
```

### Possible Errors

- `400 Bad Request`
- `401 Unauthorized`

---

## Update Billing Address

```http
PUT /billing-addresses/<address_id>
```

### Success Response

```http
200 OK
```

### Possible Errors

- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

## Delete Billing Address

```http
DELETE /billing-addresses/<address_id>
```

### Success Response

```http
204 No Content
```

### Possible Errors

- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

# Checkout

Checkout processes the products contained in the authenticated user's cart and generates an invoice.

The operation validates:

- Cart ownership.
- Cart status.
- Product availability.
- Requested quantities.
- Product stock.
- Billing information.
- Invoice creation.
- Stock reduction.
- Cart completion.
- Product cache invalidation.

A successful checkout generates an invoice and updates the corresponding product stock.

---

# Invoices

Invoices are generated by the checkout process.

They represent business records and are not created manually through a generic invoice CRUD endpoint.

## Get Invoices

```http
GET /invoices
```

Returns invoices available to the authenticated user according to their permissions.

### Success Response

```http
200 OK
```

If no invoices exist:

```json
[]
```

---

## Get Invoice by Number

```http
GET /invoices/<invoice_number>
```

Example:

```http
GET /invoices/INV-BBD354AC72DB
```

### Success Response

```http
200 OK
```

### Possible Errors

- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

# Returns

The Returns API allows customers to request product returns from their invoices and administrators to manage the return lifecycle.

Supported statuses:

```text
REQUESTED
APPROVED
REJECTED
COMPLETED
```

---

## Get Returns

```http
GET /returns
```

Returns return requests according to the authenticated user's role.

### ADMIN behavior

An `ADMIN` receives **all returns in the system**.

```http
GET /returns
Authorization: Bearer <admin_token>
```

### CLIENT behavior

A `CLIENT` receives **only their own returns**.

```http
GET /returns
Authorization: Bearer <client_token>
```

The filtering is performed using the authenticated user's ID.

### Success Response

```http
200 OK
```

Example:

```json
[
  {
    "id": 1,
    "status": "REQUESTED",
    "reason": "Product arrived damaged"
  }
]
```

If there are no returns available for the authenticated user:

```http
200 OK
```

```json
[]
```

An empty collection does not produce a `404`.

### Possible Errors

- `401 Unauthorized`

---

## Get Return by ID

```http
GET /returns/<return_id>
```

Returns a specific return request.

### ADMIN behavior

An `ADMIN` can retrieve any return.

### CLIENT behavior

A `CLIENT` can only retrieve a return associated with one of their own invoices.

### Success Response

```http
200 OK
```

### Return Does Not Exist

```http
404 Not Found
```

```json
{
  "message": "Return not found."
}
```

### CLIENT Attempts to Access Another User's Return

```http
403 Forbidden
```

```json
{
  "message": "You do not have access to this return."
}
```

---

## Create Return Request

```http
POST /returns/invoice/<invoice_number>
```

Creates a return request for one or more products from an invoice.

The authenticated client must own the invoice.

### Request Example

```json
{
  "reason": "Product arrived damaged",
  "products": [
    {
      "product_id": 1,
      "quantity": 1
    },
    {
      "product_id": 3,
      "quantity": 2
    }
  ]
}
```

### Success Response

```http
201 Created
```

The newly created return starts with:

```text
REQUESTED
```

### Validation

The service verifies:

- The invoice exists.
- The authenticated user owns the invoice.
- The requested products belong to the invoice.
- Quantities are valid.
- Previously completed returns do not cause the total returned quantity to exceed the purchased quantity.

Completed quantities are obtained with a grouped query by `invoice_product_id`, avoiding one database query for each invoice line.

### Possible Errors

- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

## Update Return Status

```http
PUT /returns/<return_id>/status
```

Updates the status of a return request.

### Role

`ADMIN`

### Request

```json
{
  "status": "APPROVED"
}
```

### Supported Status Transitions

```text
REQUESTED → APPROVED
REQUESTED → REJECTED
APPROVED  → COMPLETED
```

### Success Response

```http
200 OK
```

When a return reaches `COMPLETED` status:

- Returned quantities are registered.
- Product stock is restored.
- Invoice status is recalculated.
- Product cache entries are invalidated.

### Possible Errors

- `400 Bad Request` — Invalid status transition.
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

# Authorization Summary

| Endpoint                                 |   CLIENT    |     ADMIN      |
| ---------------------------------------- | :---------: | :------------: |
| `POST /auth/register`                    |     Yes     |      Yes       |
| `POST /auth/login`                       |     Yes     |      Yes       |
| `GET /auth/me`                           |     Yes     |      Yes       |
| `GET /users`                             |     No      |      Yes       |
| `GET /users/<id>`                        |     No      |      Yes       |
| `POST /users`                            |     No      |      Yes       |
| `PUT /users/<id>`                        |     No      |      Yes       |
| `DELETE /users/<id>`                     |     No      |      Yes       |
| `GET /products`                          |     Yes     |      Yes       |
| `GET /products/<id>`                     |     Yes     |      Yes       |
| `POST /products`                         |     No      |      Yes       |
| `PUT /products/<id>`                     |     No      |      Yes       |
| `DELETE /products/<id>`                  |     No      |      Yes       |
| `GET /carts`                             |     Own     |      Own       |
| `POST /carts`                            |     Yes     |      Yes       |
| `GET /carts/active`                      |     Own     |      Own       |
| `GET /carts/<id>`                        |     Own     |      Own       |
| `POST /carts/<id>/items`                 |     Own     |      Own       |
| `PUT /carts/<id>/items/<product_id>`     |     Own     |      Own       |
| `DELETE /carts/<id>/items/<product_id>`  |     Own     |      Own       |
| `GET /invoices`                          |     Own     | All/Authorized |
| `GET /invoices/<invoice_number>`         |     Own     |   Authorized   |
| `GET /returns`                           |     Own     |      All       |
| `GET /returns/<id>`                      |     Own     |      All       |
| `POST /returns/invoice/<invoice_number>` | Own invoice |   Authorized   |
| `PUT /returns/<id>/status`               |     No      |      Yes       |

---

# HTTP Status Codes

| Code                        | Meaning                                          | Example                                  |
| --------------------------- | ------------------------------------------------ | ---------------------------------------- |
| `200 OK`                    | Request completed successfully                   | Get products, carts, invoices or returns |
| `201 Created`               | Resource successfully created                    | Create cart                              |
| `204 No Content`            | Operation completed without response body        | Delete resource                          |
| `400 Bad Request`           | Invalid request data                             | Invalid quantity                         |
| `401 Unauthorized`          | Authentication is missing or invalid             | Missing JWT                              |
| `403 Forbidden`             | User is authenticated but lacks permission       | CLIENT accessing another user's return   |
| `404 Not Found`             | Requested resource does not exist                | No active cart                           |
| `409 Conflict`              | Request conflicts with current application state | Creating a second active cart            |
| `500 Internal Server Error` | Unexpected application error                     | Unhandled server/database error          |

---

# Redis Cache

Redis is used to cache frequently requested product information.

Examples of cache keys:

```text
products:all
product:<product_id>
```

Default TTL:

```text
600 seconds
```

Equivalent to:

```text
10 minutes
```

Relevant cache entries are invalidated when product information may have changed, including:

- Product creation.
- Product update.
- Product deletion.
- Checkout.
- Completed returns.

This prevents stale product stock or product information from being returned by the API.

---

# Important API Behavior

## Active Cart

`GET /carts/active` is a read-only operation.

It **does not create a cart**.

```text
GET /carts/active
        │
        ├── Active cart exists → 200 OK
        │
        └── No active cart     → 404 Not Found
```

A new cart must be explicitly created using:

```text
POST /carts
        │
        ├── No active cart     → 201 Created
        │
        └── Active cart exists → 409 Conflict
```

## Returns

Return visibility depends on the authenticated user's role:

```text
GET /returns

ADMIN
  └── All returns

CLIENT
  └── Only returns belonging to the authenticated user
```

For a specific return:

```text
GET /returns/<return_id>

ADMIN
  └── Can access any return

CLIENT
  ├── Own return         → 200 OK
  └── Another user's     → 403 Forbidden
```

## Empty Collections

Collection endpoints return `200 OK` with an empty array when no records are available.

Examples:

```http
GET /carts
GET /returns
GET /invoices
```

Response:

```json
[]
```

A `404 Not Found` is reserved for requests for a specific resource that does not exist, such as:

```http
GET /carts/active
GET /returns/999
GET /invoices/INV-NOT-FOUND
```
