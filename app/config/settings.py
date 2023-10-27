import logging.config
import os
from datetime import timedelta

from config import logger
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    """ Base configuration. """
    SERVICE_NAME = 'Auth'

    enable_tracer = os.environ.get('ENABLE_TRACER', 'True') == 'True'

    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

    BASE_DIR = APP_DIR

    CLIENT_SECRETS_FILE = os.path.abspath(os.path.join(APP_DIR, 'client_secret.json'))

    SERVER_NAME = os.environ.get('SERVER_NAME', '0.0.0.0')

    DB_TYPE = os.environ.get('DB_TYPE', 'postgresql')
    DB_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    DB_PORT = os.environ.get('POSTGRES_PORT')
    DB_NAME = os.environ.get('POSTGRES_DB', 'users_db')
    DB_USER = os.environ.get('POSTGRES_USER', 'app')
    DB_PASS = os.environ.get('POSTGRES_PASSWORD', '12345')

    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = os.environ.get('REDIS_PORT', '6379')

    JAEGER_HOST = os.environ.get('JAEGER_HOST', 'localhost')
    JAEGER_PORT = int(os.environ.get('JAEGER_PORT', '6831'))

    SENTRY_DSN = os.environ.get('SENTRY_DSN', '')

    SQLALCHEMY_DATABASE_URI = f'{DB_TYPE}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    JWT_COOKIE_SECURE = os.environ.get('JWT_COOKIE_SECURE', False) == 'True'
    JWT_COOKIE_CSRF_PROTECT = os.environ.get('JWT_COOKIE_CSRF_PROTECT', False) == 'True'
    JWT_TOKEN_LOCATION = os.environ.get('JWT_TOKEN_LOCATION', 'cookies')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'aaa-test')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    logging_level = os.environ.get('logging_level', 'INFO')
    secret_key = os.environ.get('secret_key', 'bbb-test')


class ProdConfig(Config):
    """ Production configuration. """
    ENV = 'prod'
    DEBUG = False


class DevConfig(Config):
    """ Development configuration. """
    ENV = 'dev'
    DEBUG = True


class TestConfig(Config):
    """ Test configuration. """
    ENV = 'test'
    TESTING = True
    DEBUG = True

