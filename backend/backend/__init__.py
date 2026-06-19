# Import Celery app so @shared_task decorators in tasks.py files
# work correctly even when running via `manage.py` commands.
from .celery import app as celery_app

__all__ = ('celery_app',)
