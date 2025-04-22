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
    is_deleted: bool


class FilesListResponse(BaseModel):
    data: List[FileResponse] = []
    limit: int = 100
    offset: int = 0
    count: int = 0
