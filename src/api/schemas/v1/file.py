from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    owner_id: UUID | None = None
    title: str
    size: int
    format: str | None = None
    created_at: datetime
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
