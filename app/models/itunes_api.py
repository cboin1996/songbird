from pydantic import BaseModel
from typing import Optional
class ItunesApiSongModel(BaseModel):
    trackName: str
    artistName: str
    collectionName: str
    artworkUrl100: str
    primaryGenreName: str
    trackNumber: str = None
    trackCount: str
    collectionId: str
    collectionArtistName: Optional[str]
    discNumber: int = None
    discCount: int = None
    releaseDate: str
    releaseDateKey: str = "releaseDate"

class ItunesApiAlbumKeys(BaseModel):
    artistName: str
    collectionName: str
    trackCount: str
    collectionId: str