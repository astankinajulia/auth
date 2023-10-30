#!/bin/bash
set -e

alembic upgrade head

gunicorn wsgi_app:app -w 4 --log-config config/gunicorn_logging.conf  -b 0.0.0.0:5000