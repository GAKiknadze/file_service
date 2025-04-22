from aioboto3 import Session

from .config import Config


async def get_s3_session():
    session = Session()
    async with session.client(
        service_name="s3",
        endpoint_url=Config.s3.path,
        region_name=Config.s3.region_name,
        aws_access_key_id=Config.s3.access_key_id,
        aws_secret_access_key=Config.s3.secret_access_key,
    ) as source:
        yield source
