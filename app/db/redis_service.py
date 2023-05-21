from __future__ import annotations

import abc
import logging
from datetime import timedelta
from typing import Any

import redis
from config.settings import Config
from db.base_cache_service import AbstractCacheService
from tracer_configurator import trace_func

log = logging.getLogger(__name__)

redis_db = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0)


class AbstractKeyValueService(abc.ABC):
    @abc.abstractmethod
    def get(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def set(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def delete(self, *args, **kwargs):
        pass


class RedisService(AbstractKeyValueService):
    def __init__(self, time: timedelta | None = None):
        self.time = time if time else Config.JWT_REFRESH_TOKEN_EXPIRES

    @staticmethod
    @trace_func
    def set(key: str, value: Any) -> None:
        redis_db.setex(name=key, time=Config.JWT_REFRESH_TOKEN_EXPIRES, value=value)

    @staticmethod
    @trace_func
    def get(key: str) -> str:
        try:
            return redis_db.get(name=key).decode('utf-8')
        except AttributeError:
            return ''

    @staticmethod
    @trace_func
    def delete(key: str) -> Any:
        return redis_db.delete(key)


class RedisCache(AbstractCacheService):
    def __init__(self):
        self.redis_service: AbstractKeyValueService = RedisService(time=Config.JWT_REFRESH_TOKEN_EXPIRES)

    def set_to_cache(self, key: str, value: Any) -> None:
        self.redis_service.set(key, value)

    def get_from_cache(self, key: str) -> str:
        return self.redis_service.get(key)

    def delete_from_cache(self, key: str) -> Any:
        return self.redis_service.delete(key)
