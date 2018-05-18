import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adictaf.settings')

app = Celery('adictaf')
app.conf.timezone = 'Africa/Nairobi'
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
