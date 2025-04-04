import os
from celery import Celery
from celery import schedules

# set the default Django settings module for the 'celery' program.
# this is also used in manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backends.settings')

app = Celery('backends')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'channel_task_runner_crontab': {
        'task': 'channel_task_runner',
        'schedule': schedules.crontab(minute=0, hour='*/12')  # every 12 hours
    },
    'refresh-zoho-tokens-every-50-minutes': {
        'task': 'refresh_zoho_tokens',
        'schedule': 60 * 50,  # 50 minutes in seconds
    },
}