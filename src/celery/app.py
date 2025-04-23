from celery import Celery

from ..core.config import Config

app = Celery(broker=Config.celery.broker)
