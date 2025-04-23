from uuid import UUID

from fastapi import APIRouter, Depends, Query, UploadFile, status
from fastapi.responses import Response, StreamingResponse

from ....celery.tasks import delete_file_from_s3_task
from ....core.database import AsyncSession, get_db
from ....core.s3 import Session, get_s3_session
from ....services.file import FileService
from ...schemas.v1.file import FileListFilters, FileResponse, FilesListResponse

router = APIRouter(tags=["files"])


@router.get("/")
async def get_files_list(
    db: AsyncSession = Depends(get_db), filters: FileListFilters = Query()
) -> FilesListResponse:
    files, count = await FileService().get_list(
        db,
        limit=filters.limit,
        offset=filters.offset,
        owner_id=filters.owner_id,
        show_deleted=filters.show_deleted,
    )
    return FilesListResponse(
        data=files, limit=filters.limit, offset=filters.offset, count=count
    )


@router.post("/")
async def upload_file(
    file: UploadFile,
    owner_id: UUID,
    db: AsyncSession = Depends(get_db),
    s3: Session = Depends(get_s3_session),
) -> FileResponse:
    return await FileService().upload(db, s3, owner_id, file.filename, file)


@router.get("/{file_id}")
async def get_file_by_id(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    s3: Session = Depends(get_s3_session),
) -> StreamingResponse:
    chunk_generator, headers = await FileService().get(db, s3, file_id)
    return StreamingResponse(
        content=chunk_generator(),
        headers=headers,
        media_type=headers.get("ContentType"),
    )


@router.get("/{file_id}/info")
async def get_file_info_by_id(
    file_id: UUID, db: AsyncSession = Depends(get_db)
) -> FileResponse:
    return await FileService().get_info(db, file_id)


@router.delete("/{file_id}")
async def delete_file_by_id(
    file_id: UUID, db: AsyncSession = Depends(get_db)
) -> Response:
    await FileService().delete(db, file_id)
    delete_file_from_s3_task.delay(file_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
