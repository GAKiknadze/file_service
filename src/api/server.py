from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..core.config import Config
from ..core.database import init_engine
from ..core.logger import logger
from ..services.file import FileService
from .exceptions import NoResultFound, handle_object_not_found
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Rest initialization - START")
    await init_engine(Config.db.uri)
    FileService().bucket_name = Config.s3.bucket_name
    FileService().chunk_size = Config.s3.chunk_size
    FileService().max_file_size = Config.s3.max_file_size
    logger.info("Rest initialization - START")
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/api")

app.add_exception_handler(
    NoResultFound, handle_object_not_found  # type:ignore[arg-type]
)
