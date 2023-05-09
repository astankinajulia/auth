#!/bin/bash
set -ex

alembic upgrade head

gunicorn wsgi_app:app -w 4 -b 0.0.0.0:5000