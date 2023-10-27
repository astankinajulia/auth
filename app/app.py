import logging
import logging.config

import click
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from comands import create_superuser_command
from config.settings import Config, DevConfig
from config import logger
from db.db_models import get_user
from flask import Flask, request
from flask_http_middleware import MiddlewareManager
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from middlewares.rate_limiter import RateLimitMiddleware
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from routes.oauth2 import oauth2_bp
from routes.roles import roles_bp
from routes.user_roles import user_roles_bp
from routes.users import user_bp
from tracer_configurator import configure_tracer


def sentry_init():
    sentry_sdk.init(
        dsn=Config.SENTRY_DSN,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )


def set_logging(app):
    # Set logging settings
    logging.config.dictConfig(logger.LOGGING_SETTINGS)
    logging.getLogger().setLevel(Config().logging_level)

    app.logger = logging.getLogger(__name__)
    # app.logger.setLevel(logging.INFO)
    # app.logger.addFilter(RequestIdFilter())


def create_app():
    sentry_init()

    app = Flask(__name__)

    # app.config.from_object(Config)
    app.config.from_object(DevConfig)

    set_logging(app)

    from db.db import db

    db.init_app(app)
    app.app_context().push()

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user_bp.login'

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    @login_manager.user_loader
    def load_user(id):
        return get_user(id)

    app.register_blueprint(user_bp, url_prefix='/auth')
    app.register_blueprint(roles_bp, url_prefix='/roles')
    app.register_blueprint(user_roles_bp, url_prefix='/users')
    app.register_blueprint(oauth2_bp, url_prefix='/oauth2')

    JWTManager(app)

    @app.cli.command('create_superuser')
    @click.argument('email')
    @click.argument('password')
    def create_superuser(email, password):
        """Create superuser."""
        create_superuser_command(email, password)

    # configure Jaeger tracer
    if Config.enable_tracer:
        configure_tracer()
        FlaskInstrumentor().instrument_app(app)

    # @app.before_request
    # def before_request():
    #     request_id = request.headers.get('X-Request-Id')
    #     if not request_id:
    #         raise RuntimeError('request id is required')

    app.wsgi_app = MiddlewareManager(app)
    app.wsgi_app.add_middleware(RateLimitMiddleware)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
