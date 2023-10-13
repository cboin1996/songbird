import logging
from fastapi import FastAPI
from fastapi.logger import logger

from .api.routers import itunes, youtube, songs
from .config import settings

app = FastAPI()
app.include_router(itunes.router)
app.include_router(youtube.router)
app.include_router(songs.router)

# configure log level based on that of uvicorn
uvicorn_logger = logging.getLogger("uvicorn.error")
logger.handlers = uvicorn_logger.handlers
logger.setLevel(uvicorn_logger.level)

@app.get("/")
async def root():
    conf = settings.SongbirdCliConfig()
    return {f"message": f"welcome to songbird v{conf.version}!"}