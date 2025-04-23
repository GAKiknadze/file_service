from asgiref.sync import async_to_sync

from celery import Celery, signals

from ..core.config import Config
from ..core.database import init_engine
from ..core.logger import logger

app = Celery(
    "file_service_worker", broker=Config.celery.broker, worker_hijack_root_logger=False
)


@signals.worker_process_init.connect
def on_start(*args, **kwargs):
    logger.info("Worker initialization - START")
    async_to_sync(init_engine)(Config.db.uri)
    logger.info("Worker initialization - END")
