from config import (
    load_private_key,
    load_public_key,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES,
)

from services.jwt_manager import JWTManager


jwt_manager = JWTManager(
    private_key=load_private_key(),
    public_key=load_public_key(),
    algorithm=JWT_ALGORITHM,
    access_token_expires=JWT_ACCESS_TOKEN_EXPIRES
)


payload = {
    "id": 1,
    "role": "ADMIN"
}


token = jwt_manager.encode(payload)

print("\nGenerated token:")
print(token)


decoded_payload = jwt_manager.decode(token)

print("\nDecoded payload:")
print(decoded_payload)


assert decoded_payload["id"] == payload["id"]
assert decoded_payload["role"] == payload["role"]

print("\nJWT test passed successfully.")