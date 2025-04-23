from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound


async def handle_object_not_found(req: Request, exc: NoResultFound) -> JSONResponse:
    return JSONResponse(
        content={"msg": "Object not found"}, status_code=status.HTTP_404_NOT_FOUND
    )
