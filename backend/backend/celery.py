"""
Celery application entry point.

Rules:
  - All tasks must be short-lived or split into subtasks.
  - Never block the request cycle — dispatch tasks, don't run them inline.
  - Tasks should be idempotent where possible.
  - Use CELERY_TASK_ALWAYS_EAGER=True in development (see settings/development.py).
"""
import os

from celery import Celery

# Default to development when running celery CLI directly.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.development')

app = Celery('sanad')

# Read all CELERY_* settings from Django settings with the CELERY namespace.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all INSTALLED_APPS that have a tasks.py module.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Health-check task — useful in tests and monitoring."""
    print(f'Request: {self.request!r}')
