#!/bin/bash

# Ensure the virtual environment is activated
export PATH="/app/.venv/bin:$PATH"
source .venv/bin/activate

# Start Django server in the background
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000 &

# Start Celery worker
echo "Starting Celery worker..."
xvfb-run -a celery -A app worker --loglevel=info
