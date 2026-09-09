from datetime import datetime, timedelta, UTC

import jwt


class JWTManager:

    def __init__(
        self,
        private_key: str,
        public_key: str,
        algorithm: str = "RS256",
        access_token_expires: int = 900
    ):
        self.private_key = private_key
        self.public_key = public_key
        self.algorithm = algorithm
        self.access_token_expires = access_token_expires

    def encode(self, payload: dict) -> str:
        now = datetime.now(UTC)

        token_payload = {
            **payload,
            "iat": now,
            "exp": now + timedelta(
                seconds=self.access_token_expires
            )
        }

        return jwt.encode(
            token_payload,
            self.private_key,
            algorithm=self.algorithm
        )

    def decode(self, token: str) -> dict:
        return jwt.decode(
            token,
            self.public_key,
            algorithms=[self.algorithm]
        )