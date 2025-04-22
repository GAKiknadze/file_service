from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import StreamingResponse

from ...schemas.v1.file import FileResponse, FilesListResponse
from ....services.file import FileService
from ....core.database import get_db, AsyncSession
from ....core.s3 import get_s3_session, Session


router = APIRouter(tags=["files"])


@router.get("/")
async def get_files_list(db: AsyncSession = Depends(get_db)) -> FilesListResponse:
    files, count = await FileService().get_list(db)
    return FilesListResponse(data=files, count=count)


@router.post("/")
async def upload_file(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    s3: Session = Depends(get_s3_session)
) -> FileResponse:
    owner_id = uuid4()  # Заглушка
    return await FileService().upload(db, s3, owner_id, file.filename, file)


@router.get("/{file_id}")
async def get_file_by_id(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    s3: Session = Depends(get_s3_session)
) -> StreamingResponse:
    chunk_generator, headers = await FileService().get(db, s3, file_id)
    return StreamingResponse(
        content=chunk_generator(),
        headers=headers,
        media_type=headers.get("ContentType")
    )


@router.get("/{file_id}/info")
async def get_file_info_by_id(file_id: UUID, db: AsyncSession = Depends(get_db)) -> FileResponse:
    return await FileService().get_info(db, file_id)


@router.delete("/{file_id}")
async def delete_file_by_id(file_id: UUID, db: AsyncSession = Depends(get_db)) -> None:
    await FileService().delete(db, file_id)
