#!/bin/sh

python manage.py migrate

python manage.py collectstatic --noinput

gunicorn ckstock.wsgi -b 0.0.0.0:8000