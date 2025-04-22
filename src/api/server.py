from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..core.config import Config
from ..core.database import init_engine
from ..services.file import FileService
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_engine(Config.db.uri)
    FileService().set_bucket_name(Config.s3.bucket_name)
    FileService().set_chunk_size(Config.s3.chunk_size)
    FileService().set_max_file_size(Config.s3.max_file_size)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/api")
