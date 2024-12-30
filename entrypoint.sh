#!/bin/bash

# Activate Poetry virtual environment
export PATH="/app/.venv/bin:$PATH"
source .venv/bin/activate

echo "Starting Celery worker..."
xvfb-run celery -A app worker --loglevel=info &

echo "Starting Django server..."
poetry shell
python manage.py runserver 0.0.0.0:8000
