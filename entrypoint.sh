#!/bin/bash

# Start Redis
poetry shell &
redis-server &

# Start Django with Daphne (or manage.py runserver)
daphne -u /tmp/daphne.sock app.asgi:application &

# Start Celery worker
celery -A app worker --loglevel=info
