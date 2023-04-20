import logging
from typing import Any

import redis

from config.settings import Config

log = logging.getLogger(__name__)

redis_db = redis.Redis(host='0.0.0.0', port=6379, db=0)


class Redis:
    def __init__(self):
        self.redis_db = redis_db

    @staticmethod
    def set(key: str, value: Any) -> None:
        redis_db.setex(name=key, time=Config.JWT_REFRESH_TOKEN_EXPIRES, value=value)

    @staticmethod
    def get(key: str) -> str:
        return redis_db.get(name=key).decode("utf-8")

    @staticmethod
    def delete(key: str) -> Any:
        return redis_db.delete(key)
