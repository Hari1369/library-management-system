# import os
# from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')

# app = Celery('library_system')
# app.config_from_object('django.conf:settings', namespace='CELERY')

# app.conf.broker_url = os.environ.get('CELERY_BROKER_URL')
# app.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND')

# app.autodiscover_tasks()

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_system.settings")

app = Celery("library_system")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()