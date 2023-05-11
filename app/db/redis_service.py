import logging
from typing import Any

import redis
from config.settings import Config
from db.base_cache_service import AbstractCacheService

log = logging.getLogger(__name__)

redis_db = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0)


class RedisDB(AbstractCacheService):
    def __init__(self):
        self.redis_db = redis_db

    @staticmethod
    def set_to_cache(key: str, value: Any) -> None:
        redis_db.setex(name=key, time=Config.JWT_REFRESH_TOKEN_EXPIRES, value=value)

    @staticmethod
    def get_from_cache(key: str) -> str:
        return redis_db.get(name=key).decode("utf-8")

    @staticmethod
    def delete_from_cache(key: str) -> Any:
        return redis_db.delete(key)
