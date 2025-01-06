from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
os.environ.setdefault("FORKED_BY_MULTIPROCESSING", "1")

# Create the Celery app
app = Celery("app")

# Load task modules from all registered Django app configs
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks
app.autodiscover_tasks()

# Example periodic task configuration (runs daily at midnight)
app.conf.beat_schedule = {
    "my_periodic_task": {
        "task": "core.tasks.my_periodic_task",
        "schedule": crontab(minute=0, hour=0),  # Executes every midnight
    },
}


# Debug task to check worker functionality
@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
