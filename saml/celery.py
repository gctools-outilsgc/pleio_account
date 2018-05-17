from __future__ import absolute_import, unicode_literals
import os
from django.conf import settings
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'concierge.settings')

app = Celery('saml', broker=settings.CELERY_BROKER_URL)

if __name__ == '__main__':
    app.start()
