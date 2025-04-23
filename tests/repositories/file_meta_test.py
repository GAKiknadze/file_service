from uuid import uuid4

import pytest
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.file_meta import FileMetaEntity
from src.repositories.file_meta import FileMetaRepository


@pytest.fixture
async def file_meta(db: AsyncSession) -> FileMetaEntity:
    """Create a test file metadata record"""
    file = await FileMetaRepository.create(
        db=db,
        internal_id="test123",
        owner_id=uuid4(),
        title="test.txt",
        size=1000,
        format="txt",
    )
    return file


async def test_create_file_meta(db: AsyncSession):
    """Test creating a new file metadata record"""
    owner_id = uuid4()
    file = await FileMetaRepository.create(
        db=db,
        internal_id="test123",
        owner_id=owner_id,
        title="test.txt",
        size=1000,
        format="txt",
    )

    assert isinstance(file, FileMetaEntity)
    assert file.internal_id == "test123"
    assert file.owner_id == owner_id
    assert file.title == "test.txt"
    assert file.size == 1000
    assert file.format == "txt"
    assert file.is_deleted is False


async def test_create_file_meta_minimal(db: AsyncSession):
    """Test creating a file metadata record with minimal required fields"""
    file = await FileMetaRepository.create(
        db=db,
        internal_id="test123",
        owner_id=None,
        title="minimal.txt",
        size=0,
    )

    assert isinstance(file, FileMetaEntity)
    assert file.internal_id == "test123"
    assert file.owner_id is None
    assert file.title == "minimal.txt"
    assert file.size == 0
    assert file.format is None
    assert file.is_deleted is False


async def test_get_by_id(db: AsyncSession, file_meta: FileMetaEntity):
    """Test retrieving a file metadata record by ID"""
    retrieved_file = await FileMetaRepository.get_by_id(db, file_meta.id)

    assert retrieved_file is not None
    assert retrieved_file.id == file_meta.id
    assert retrieved_file.title == file_meta.title


async def test_get_by_id_not_found(db: AsyncSession):
    """Test retrieving a non-existent file metadata record"""
    non_existent_id = uuid4()
    with pytest.raises(NoResultFound) as exc_info:
        await FileMetaRepository.get_by_id(db, non_existent_id)
    assert exc_info.errisinstance(NoResultFound)


async def test_get_list(db: AsyncSession, file_meta: FileMetaEntity):
    """Test retrieving a list of file metadata records"""
    owner_id = uuid4()
    await FileMetaRepository.create(
        db=db, internal_id="test456", owner_id=owner_id, title="another.txt", size=2000
    )

    files, count = await FileMetaRepository.get_list(
        db, limit=10, offset=0, owner_id=owner_id
    )

    assert isinstance(files, list)
    assert count >= 1
    assert all(isinstance(f, FileMetaEntity) for f in files)
    assert all(f.owner_id == owner_id for f in files)


async def test_get_list_pagination(db: AsyncSession):
    """Test pagination behavior of get_list"""
    owner_id = uuid4()
    for i in range(15):
        await FileMetaRepository.create(
            db=db,
            internal_id=f"test{i}",
            owner_id=owner_id,
            title=f"file{i}.txt",
            size=1000,
        )

    files_page1, count1 = await FileMetaRepository.get_list(
        db, limit=5, offset=0, owner_id=owner_id
    )
    assert len(files_page1) == 5
    assert count1 >= 15

    files_page2, count2 = await FileMetaRepository.get_list(
        db, limit=5, offset=5, owner_id=owner_id
    )
    assert len(files_page2) == 5
    assert count2 == count1

    page1_ids = {f.id for f in files_page1}
    page2_ids = {f.id for f in files_page2}
    assert not page1_ids.intersection(page2_ids)


async def test_get_list_empty_result(db: AsyncSession):
    """Test get_list with filters that return no results"""
    non_existent_owner = uuid4()
    files, count = await FileMetaRepository.get_list(db, owner_id=non_existent_owner)

    assert isinstance(files, list)
    assert len(files) == 0
    assert count == 0


async def test_delete_by_id(db: AsyncSession, file_meta: FileMetaEntity):
    """Test marking a file metadata record as deleted"""
    await FileMetaRepository.delete_by_id(db, file_meta.id)
    await db.commit()

    deleted_file = await FileMetaRepository.get_by_id(db, file_meta.id)
    assert deleted_file is not None
    assert deleted_file.is_deleted is True


async def test_delete_by_id_permanent(db: AsyncSession, file_meta: FileMetaEntity):
    """Test permanent deletion of a file metadata record"""
    await FileMetaRepository.delete_by_id(db, file_meta.id, mark=False)
    await db.commit()

    deleted_file = await FileMetaRepository.get_by_id(db, file_meta.id)
    assert deleted_file is not None
    assert deleted_file.deleted_at is not None


async def test_get_list_show_deleted(db: AsyncSession):
    """Test retrieving list with deleted files"""
    owner_id = uuid4()
    for i in range(5):
        await FileMetaRepository.create(
            db=db,
            internal_id=f"test{i}",
            owner_id=owner_id,
            title=f"file{i}.txt",
            size=1000,
        )
    await db.commit()

    files, _ = await FileMetaRepository.get_list(db, owner_id=owner_id)
    await FileMetaRepository.delete_by_id(db, files[0].id)
    await db.commit()
    await FileMetaRepository.delete_by_id(db, files[1].id)
    await db.commit()

    files_hidden, _ = await FileMetaRepository.get_list(
        db, owner_id=owner_id, show_deleted=False
    )
    files_shown, _ = await FileMetaRepository.get_list(
        db, owner_id=owner_id, show_deleted=True
    )

    assert len(files_shown) > len(files_hidden)
