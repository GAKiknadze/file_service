from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class FileResponse(BaseModel):
    id: UUID
    title: str
    size: int
    format: str
    created_at: datetime
    deleted_at: datetime | None = None
    is_deleted: bool


class FileListFilters(BaseModel):
    owner_id: UUID | None = None
    show_deleted: bool = False
    limit: int = 10
    offset: int = 0


class FilesListResponse(BaseModel):
    data: List[FileResponse] = []
    limit: int = 100
    offset: int = 0
    count: int = 0
