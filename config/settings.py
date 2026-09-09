import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

CACHE_TTL = int(
    os.getenv("CACHE_TTL", "600")
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "RS256"
)

JWT_ACCESS_TOKEN_EXPIRES = int(
    os.getenv(
        "JWT_ACCESS_TOKEN_EXPIRES",
        "900"
    )
)


if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required."
    )

if not REDIS_URL:
    raise ValueError(
        "REDIS_URL environment variable is required."
    )


def load_private_key() -> str:
    path = BASE_DIR / "keys" / "private.pem"

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


def load_public_key() -> str:
    path = BASE_DIR / "keys" / "public.pem"

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()