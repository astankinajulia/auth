import abc


class AbstractCacheService(abc.ABC):
    @abc.abstractmethod
    async def get_from_cache(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def set_to_cache(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def delete_from_cache(self, *args, **kwargs):
        pass
