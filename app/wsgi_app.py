from gevent import monkey
monkey.patch_all()

from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware

from app import create_app  # noqa

app = SentryWsgiMiddleware(create_app())
