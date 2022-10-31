import os
import sys
from datetime import datetime
from typing import List, Optional

import pydantic
from pydantic import BaseModel, BaseSettings


class ItunesApiSongKeys:
    track_name = "trackName"
    artist_name = "artistName"
    collection_name = "collectionName"
    artworkUrl100 = "artworkUrl100"
    primary_genre_name = "primaryGenreName"
    track_num = "trackNumber"
    track_count = "trackCount"
    collection_id = "collectionId"
    collection_artist_name = "collectionArtistName"
    disc_num = "discNumber"
    disc_count = "discCount"
    release_date = "releaseDate"

    def required_song_keys(self):
        return [
            track_name,
            artist_name,
            collection_name,
            artworkUrl100,
            primary_genre_name,
            track_name,
            track_count,
            disc_num,
            disc_count,
            release_date,
        ]

    def required_album_keys(self):
        return [artist_name, collection_name, track_count, collection_id]


class SongbirdConfig(BaseSettings):
    """Configuration using .env file or defaults declared in here"""

    itunes_search_api_base_url: str = "https://itunes.apple.com/search"
    itunes_enabled: bool = True
    itunes_path_str: Optional[str] = None
    itunes_api_keys: ItunesApiSongKeys = ItunesApiSongKeys()
    gdrive_enabled: bool = False
    gdrive_path_str: Optional[str] = None
    gdrive_secret_path_str: Optional[str] = None
    local_song_store_str: str = "dump"
