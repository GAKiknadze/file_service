from uuid import UUID

from fastapi import APIRouter, Depends, Query, UploadFile, status
from fastapi.responses import Response, StreamingResponse

from ....celery.tasks import delete_file_from_s3_task
from ....core.database import AsyncSession, get_db
from ....core.s3 import Session, get_s3_session
from ....services.file import FileService
from ...schemas.v1.file import FileListFilters, FileResponse, FilesListResponse

router = APIRouter(tags=["files"])


@router.get("/", response_model=FilesListResponse, status_code=status.HTTP_200_OK)
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
        data=files,  # type:ignore[arg-type]
        limit=filters.limit,
        offset=filters.offset,
        count=count,
    )


@router.post("/", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    owner_id: UUID,
    db: AsyncSession = Depends(get_db),
    s3: Session = Depends(get_s3_session),
) -> FileResponse:
    obj = await FileService().upload(
        db, s3, owner_id, file.filename or "unnamed_file", file
    )  # type:ignore[arg-type]
    return FileResponse.model_validate(obj)


@router.get(
    "/{file_id}", response_class=StreamingResponse, status_code=status.HTTP_200_OK
)
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


@router.get(
    "/{file_id}/info", response_model=FileResponse, status_code=status.HTTP_200_OK
)
async def get_file_info_by_id(
    file_id: UUID, db: AsyncSession = Depends(get_db)
) -> FileResponse:
    obj = await FileService().get_info(db, file_id)
    return FileResponse.model_validate(obj)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_by_id(
    file_id: UUID, db: AsyncSession = Depends(get_db)
) -> Response:
    await FileService().delete(db, file_id)
    delete_file_from_s3_task.delay(file_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
