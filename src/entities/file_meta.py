from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.orm as so

from . import Base


class FileMetaEntity(Base):
    __tablename__ = "file_meta"

    id: so.Mapped[UUID] = so.mapped_column(sa.UUID(), primary_key=True, default=uuid4)
    internal_id: so.Mapped[str] = so.mapped_column(sa.String(255), index=True, nullable=True)
    owner_id: so.Mapped[UUID] = so.mapped_column(sa.UUID())
    title: so.Mapped[str] = so.mapped_column(sa.String(255))
    size: so.Mapped[int] = so.mapped_column(sa.Integer())
    format: so.Mapped[str] = so.mapped_column(sa.String(255))
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), default=sa.func.now()
    )
    deleted_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True))
    is_deleted: so.Mapped[bool] = so.mapped_column(sa.Boolean(), default=False)
