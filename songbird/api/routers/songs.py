from fastapi import APIRouter
from fastapi.logger import logger
import logging

uvicorn_logger = logging.getLogger("uvicorn.error")
logger.handlers = uvicorn_logger.handlers
logger.setLevel(uvicorn_logger.level)

# add router for all songbird related api calls
router = APIRouter(
    prefix="/songs",
    tags=["songs"],
)


@router.get("/songs", response_model=None)
async def songs():
    pass