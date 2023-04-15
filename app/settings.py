import os
from datetime import timedelta
from pathlib import Path


class Config(object):
    """Base configuration."""

    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

    BASE_DIR = APP_DIR

    DB_TYPE = os.environ.get('DB_TYPE', 'postgresql')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_TYPE', '5439')
    DB_NAME = os.environ.get('POSTGRES_DB', 'users_db')
    DB_USER = os.environ.get('POSTGRES_USER', 'app')
    DB_PASS = os.environ.get('POSTGRES_PASSWORD', '12345')

    SQLALCHEMY_DATABASE_URI = f'{DB_TYPE}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    JWT_COOKIE_SECURE = os.environ.get('JWT_COOKIE_SECURE', True) == 'True'
    JWT_TOKEN_LOCATION = os.environ.get('JWT_TOKEN_LOCATION', 'cookies')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'aaa-test')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = False


class DevConfig(Config):
    """Development configuration."""
    ENV = 'dev'
    DEBUG = True


class TestConfig(Config):
    """ Тестовая конфигурация. """
    ENV = 'test'
    TESTING = True
    DEBUG = True
