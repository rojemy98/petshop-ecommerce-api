import redis


class CacheManager:

    def __init__(self, redis_url: str):
        self.client = redis.from_url(
            redis_url,
            decode_responses=True
        )

    def get_data(self, key: str) -> str | None:
        return self.client.get(key)

    def store_data(
        self,
        key: str,
        value: str,
        expiration: int
    ) -> None:

        self.client.setex(
            key,
            expiration,
            value
        )

    def delete_data(self, key: str) -> None:
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        return bool(
            self.client.exists(key)
        )

    def ping(self) -> bool:
        return self.client.ping()