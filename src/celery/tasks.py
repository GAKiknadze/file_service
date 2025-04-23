from uuid import UUID
import traceback

from asgiref.sync import async_to_sync

from celery import shared_task

from ..core.logger import logger
from ..core.config import Config
from ..core.database import get_db
from ..core.s3 import get_s3_session
from ..services.file import FileService


async def delete_file_from_s3(file_id: UUID):
    async for s3_session in get_s3_session():
        async for db in get_db():
            try:
                obj = await FileService().get_info(db, file_id)
                if not obj.is_deleted:
                    return

                await s3_session.delete_object(Bucket=Config.s3.bucket_name, Key=obj.internal_id)
                await FileService().delete(db, file_id, mark=False)
            except Exception:
                logger.warning(traceback.format_exc())


@shared_task(name="delete_file_from_s3", ignore_result=True)
def delete_file_from_s3_task(file_id: UUID):
    async_to_sync(delete_file_from_s3)(file_id)
