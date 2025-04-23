from mimetypes import guess_extension, guess_type
from typing import Any, AsyncGenerator, Sequence, Tuple
from urllib.parse import quote
from uuid import UUID, uuid4

from aioboto3 import Session
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..entities.file_meta import FileMetaEntity
from ..repositories.file_meta import FileMetaRepository
from ..utils import singleton


@singleton
class FileService:
    _max_file_size: int = 0
    _chunk_size: int = 5 * 1024 * 1024  # 5MB
    _bucket_name: str = "test_bucket"

    @property
    def max_file_size(self) -> int:
        return self._max_file_size

    @max_file_size.setter
    def max_file_size(self, value: int) -> None:
        self._max_file_size = value

    @property
    def chunk_size(self) -> int:
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value: int) -> None:
        self._chunk_size = value

    @property
    def bucket_name(self) -> str:
        return self._bucket_name

    @bucket_name.setter
    def bucket_name(self, value: str) -> None:
        self._bucket_name = value

    @staticmethod
    def _get_uuid_file_name(file_id: UUID, mime_type: str | None = None) -> str:
        if not mime_type:
            return str(file_id)

        if mime_type == "application/octet-stream":
            extension = ".bin"
        else:
            extension = guess_extension(mime_type) or ""
        return f"{file_id}{extension}"

    async def upload(
        self,
        db: AsyncSession,
        s3: Session,
        owner_id: UUID,
        filename: str,
        file: UploadFile,
    ) -> FileMetaEntity:
        content_type = file.content_type
        if content_type is None:
            content_type, _ = guess_type(filename)
        file_id = self._get_uuid_file_name(uuid4(), content_type)
        mpu = await s3.create_multipart_upload(
            Bucket=self._bucket_name, Key=file_id, ContentType=content_type
        )

        upload_id = mpu["UploadId"]
        parts = []
        part_number = 1
        file_size = 0
        try:
            while True:
                chunk = await file.read(self._chunk_size)
                if not chunk:
                    break
                file_size += self._chunk_size
                if self._max_file_size != 0 and file_size > self._max_file_size:
                    raise Exception("File too large")

                part = await s3.upload_part(
                    Bucket=self._bucket_name,
                    Key=file_id,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=chunk,
                )
                parts.append({"PartNumber": part_number, "ETag": part["ETag"]})
                part_number += 1

            await s3.complete_multipart_upload(
                Bucket=self._bucket_name,
                Key=file_id,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )
        except Exception as e:
            await s3.abort_multipart_upload(
                Bucket=self._bucket_name, Key=file_id, UploadId=upload_id
            )
            raise e

        return await FileMetaRepository.create(
            db, file_id, owner_id, filename, size=file_size, format=content_type
        )

    async def get(
        self, db: AsyncSession, s3: Session, _id: UUID
    ) -> Tuple[AsyncGenerator[bytes, None], dict[str, Any]]:
        obj = await FileMetaRepository.get_by_id(db, _id)
        if obj.internal_id is None:
            raise Exception("File not found")

        try:
            head = await s3.head_object(Bucket=self._bucket_name, Key=obj.internal_id)
        except s3.exceptions.NoSuchKey:
            raise Exception("File not found")

        file_size = head["ContentLength"]
        content_type = head.get("ContentType", "application/octet-stream")
        filename = obj.title

        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}",
            "Content-Length": str(file_size),
            "Content-Type": content_type,
        }

        async def chunk_generator():
            try:
                response = await s3.get_object(
                    Bucket=self._bucket_name, Key=obj.internal_id
                )
                async with response["Body"] as stream:
                    body = await stream.read()
                    yield body
            except Exception as e:
                raise Exception(f"Download error: {str(e)}")

        return chunk_generator, headers

    async def get_info(self, db: AsyncSession, _id: UUID) -> FileMetaEntity:
        """
        Retrieve file metadata information by its unique identifier.

        Args:
            db (AsyncSession): The asynchronous database session to use for the query.
            _id (UUID): The unique identifier of the file.

        Returns:
            FileMetaEntity: The metadata entity of the file corresponding to the given ID.

        Raises:
            Exception: If the file with the given ID is not found or any database error occurs.
        """
        return await FileMetaRepository.get_by_id(db, _id)

    async def get_list(
        self,
        db: AsyncSession,
        limit: int = 10,
        offset: int = 0,
        owner_id: UUID | None = None,
        show_deleted: bool = False,
    ) -> Tuple[Sequence[FileMetaEntity], int]:
        """
        Retrieve a list of file metadata entities with pagination and filtering options.

        Args:
            db (AsyncSession): The database session to use for the query.
            limit (int, optional): The maximum number of records to retrieve. Defaults to 10.
            offset (int, optional): The number of records to skip before starting to retrieve. Defaults to 0.
            owner_id (UUID | None, optional): Filter files by the owner's ID. Defaults to None.
            show_deleted (bool, optional): Whether to include deleted files in the results. Defaults to False.

        Returns:
            Tuple[Sequence[FileMetaEntity], int]: A tuple containing a sequence of file metadata entities
            and the total count of records matching the query.
        """
        return await FileMetaRepository.get_list(
            db, limit=limit, offset=offset, owner_id=owner_id, show_deleted=show_deleted
        )

    async def delete(self, db: AsyncSession, _id: UUID, mark: bool = True) -> None:
        await FileMetaRepository.delete_by_id(db, _id, mark=mark)
