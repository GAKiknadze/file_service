from uuid import UUID

from asgiref.sync import async_to_sync

from celery import shared_task

from ..core.config import Config
from ..core.database import get_db
from ..core.s3 import get_s3_session
from ..services.file import FileService


async def delete_file_from_s3(file_id: UUID):
    async with get_s3_session() as s3_session, get_db() as db:
        try:
            obj = await FileService().get_info(db, file_id)
            if not obj.is_deleted:
                return

            await s3_session.Object(Config.s3.bucket_name, obj.internal_id).delete()
            await FileService().delete(db, file_id, mark=False)
        except Exception:
            pass


@shared_task(name="delete_file_from_s3", ignore_result=True)
async def delete_file_from_s3_task(file_id: UUID):
    async_to_sync(delete_file_from_s3_task)(file_id)
