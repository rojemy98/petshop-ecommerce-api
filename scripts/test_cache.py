from cache import CacheManager
from config import REDIS_URL


cache = CacheManager(
    REDIS_URL
)

print(
    "Redis connected:",
    cache.ping()
)

cache.store_data(
    "test:key",
    "Hello Redis",
    60
)

print(
    "Value:",
    cache.get_data("test:key")
)

print(
    "Exists:",
    cache.exists("test:key")
)

cache.delete_data(
    "test:key"
)

print(
    "After delete:",
    cache.get_data("test:key")
)