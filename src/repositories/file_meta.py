from typing import Sequence, Tuple
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..entities.file_meta import FileMetaEntity


class FileMetaRepository:
    """
    This repository provides methods for interacting with the `FileMetaEntity` table in the database.
    It includes functionality for retrieving, creating, and deleting file metadata records.
    """

    @staticmethod
    async def get_list(
        db: AsyncSession,
        limit: int = 10,
        offset: int = 0,
        owner_id: UUID | None = None,
        show_deleted: bool = False,
    ) -> Tuple[Sequence[FileMetaEntity], int]:
        """
        Retrieve a list of FileMetaEntity records from the database with optional filtering,
        pagination, and total count.
        Args:
            db (AsyncSession): The database session to use for the query.
            limit (int, optional): The maximum number of records to retrieve. Defaults to 10.
            offset (int, optional): The number of records to skip before starting to collect the result set. Defaults to 0.
            owner_id (UUID | None, optional): Filter records by the owner's UUID. Defaults to None.
            show_deleted (bool, optional): Whether to include deleted records in the result set. Defaults to False.
        Returns:
            Tuple[Sequence[FileMetaEntity], int]: A tuple containing:
                - A sequence of FileMetaEntity records matching the query.
                - The total count of records matching the query (ignoring pagination).
        """
        query = select(FileMetaEntity)

        if owner_id:
            query = query.where(FileMetaEntity.owner_id == owner_id)

        if not show_deleted:
            query = query.where(FileMetaEntity.is_deleted.is_(False))

        count_query = select(func.count()).select_from(query.subquery())
        total_count = (await db.execute(count_query)).scalar() or 0

        query = (
            query.order_by(FileMetaEntity.created_at.desc()).limit(limit).offset(offset)
        )
        result = await db.execute(query)
        records = result.scalars().all()

        return records, total_count

    @staticmethod
    async def create(
        db: AsyncSession,
        internal_id: str,
        owner_id: UUID,
        title: str,
        size: int = 0,
        format: str | None = None,
    ) -> FileMetaEntity:
        """
        Creates a new FileMetaEntity record in the database.

        Args:
            db (AsyncSession): The database session to use for the operation.
            owner_id (UUID): The unique identifier of the owner of the file.
            title (str): The title of the file.
            size (int, optional): The size of the file in bytes. Defaults to 0.
            format (str, optional): The format or extension of the file. Defaults to None.

        Returns:
            FileMetaEntity: The newly created FileMetaEntity object.
        """
        obj = FileMetaEntity(
            internal_id=internal_id,
            owner_id=owner_id,
            title=title,
            size=size,
            format=format,
        )
        db.add(obj)
        await db.commit()
        return obj

    @staticmethod
    async def get_by_id(db: AsyncSession, _id: UUID) -> FileMetaEntity:
        """
        Retrieve a FileMetaEntity by its unique identifier.

        Args:
            db (AsyncSession): The database session to use for the query.
            _id (UUID): The unique identifier of the FileMetaEntity to retrieve.

        Returns:
            FileMetaEntity | None: The FileMetaEntity instance if found, otherwise None.
        """
        return await db.get_one(FileMetaEntity, _id)

    @staticmethod
    async def delete_by_id(db: AsyncSession, _id: UUID, mark: bool = True) -> None:
        """
        Deletes a file metadata record from the database by its ID.

        Args:
            db (AsyncSession): The asynchronous database session to use for executing the query.
            _id (UUID): The unique identifier of the file metadata record to delete.

        Returns:
            None
        """
        stmt = update(FileMetaEntity).where(FileMetaEntity.id == _id)

        if mark:
            stmt = stmt.values(is_deleted=True)
        else:
            stmt = stmt.values(deleted_at=func.now())

        await db.execute(stmt)
        await db.commit()
