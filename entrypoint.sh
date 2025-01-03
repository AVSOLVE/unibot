#!/bin/bash

echo "Collect static files..."
python manage.py collectstatic --noinput

echo "Apply database migrations..."
python manage.py makemigrations
python manage.py migrate

exec "$@"
