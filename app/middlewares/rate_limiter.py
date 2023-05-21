import datetime
import logging

from db.redis_service import AbstractKeyValueService, RedisService
from flask_http_middleware import BaseHTTPMiddleware
from flask_restx import abort

log = logging.getLogger(__name__)

MAX_TOKENS_IN_BUCKET = 20

TOKENS_TO_ADD = 1
TIME_UNIT_SECONDS = 60
TOKENS_PER_TIME = TOKENS_TO_ADD / TIME_UNIT_SECONDS

RATE_LIMIT_TOKEN_EXPIRES = datetime.timedelta(minutes=60)

FORMAT = '%Y-%m-%d %H:%M:%S.%f'


key_value_storage: AbstractKeyValueService = RedisService(time=RATE_LIMIT_TOKEN_EXPIRES)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self):
        super().__init__()

    def dispatch(self, request, call_next):
        request_id = request.headers.get('X-Request-Id')
        can_make_request = rate_limiter_token_bucket(request_id)
        if not can_make_request:
            abort(429, message='Too many requests. Try again later.')
        response = call_next(request)
        return response


def rate_limiter_token_bucket(request_id):
    """Rate limiter with Redis. Token bucket algorithm."""

    now = datetime.datetime.utcnow()

    # get from redis number tokens in the bucket and last check time
    key_bucket = f'{request_id}_bucket'
    key_time = f'{request_id}_time'

    bucket = key_value_storage.get(key_bucket)
    if bucket:
        bucket = int(bucket)
    else:
        bucket = MAX_TOKENS_IN_BUCKET

    try:
        last_check = datetime.datetime.strptime(key_value_storage.get(key_time), FORMAT)
    except ValueError:
        last_check = now

    # calculate token increment
    time_passed = now - last_check
    bucket = bucket + int(time_passed.seconds * TOKENS_PER_TIME)

    if bucket > MAX_TOKENS_IN_BUCKET:
        bucket = MAX_TOKENS_IN_BUCKET

    if bucket < 1:
        log.info('No tokens in the bucket request_id={}'.format(request_id))
        result = False
    else:
        bucket = bucket - 1
        result = True

    key_value_storage.set(key_bucket, bucket)
    if time_passed.seconds > TIME_UNIT_SECONDS:
        key_value_storage.set(key_time, str(now))

    return result
