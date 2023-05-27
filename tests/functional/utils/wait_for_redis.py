import os

from helpers import backoff
from redis import Redis

if __name__ == '__main__':

    @backoff()
    def connect_to_redis():
        redis_client = Redis(host=os.environ.get("REDIS_HOST"), port=int(os.environ.get("REDIS_PORT")))

        return redis_client
