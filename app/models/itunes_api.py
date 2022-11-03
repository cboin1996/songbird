from pydantic import BaseModel
from typing import Optional


class ItunesApiSongModel(BaseModel):
    trackName: str
    artistName: str
    collectionName: str
    artworkUrl100: str
    primaryGenreName: str
    trackNumber: int
    trackCount: int
    collectionId: str = ""
    collectionArtistName: str = ""
    discNumber: int
    discCount: int
    releaseDate: str
    releaseDateKey: str = "releaseDate"

class ItunesApiAlbumKeys(BaseModel):
    artistName: str
    collectionName: str
    trackCount: int
    collectionId: str
