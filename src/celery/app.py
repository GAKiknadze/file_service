from asgiref.sync import async_to_sync

from celery import Celery, signals

from ..core.config import Config
from ..core.database import init_engine

app = Celery(broker=Config.celery.broker)


@signals.worker_process_init.connect
def on_start(*args, **kwargs):
    async_to_sync(init_engine)(Config.db.uri)
