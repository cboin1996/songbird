import os
import sys
from datetime import datetime
from typing import List, Optional

import pydantic
from pydantic import BaseModel, BaseSettings
import sys

from models import itunes_api


class SongbirdConfig(BaseSettings):
    """Configuration using .env file or defaults declared in here"""

    run_local: bool = False
    root_path: str = sys.path[0]
    itunes_search_api_base_url: str = "https://itunes.apple.com/search"
    itunes_enabled: bool = True
    itunes_folder_path: Optional[str] = "itunes"
    itunes_lib_path: Optional[str] = ""
    gdrive_enabled: bool = False
    gdrive_folder_path: Optional[str] = None
    gdrive_secret_path_str: Optional[str] = None
    local_song_store_str: str = "dump"

    def get_local_folder_path(self):
        return os.path.join(self.root_path, self.local_song_store_str)

    def get_itunes_folder_path(self):
        """If you run the app locally, configure the gdrive path as an absolute path. Otherwise, the program will
        use the local container storage and assume to be running in a docker container.

        Returns:
            str: the path to where itunes destined songs should live
        """
        if run_local:
            return itunes_folder_path
        return os.path.join(self.root_path, self.itunes_folder_path)

    def get_gdrive_folder_path(self):
        if run_local:
            return gdrive_folder_path
        return os.path.join(self.root_path, self.gdrive_folder_path)
