import os
import sys
from datetime import datetime
from typing import List, Optional

import pydantic
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings
import sys


class SongbirdCliConfig(BaseSettings):
    """Configuration using .env file or defaults declared in here"""

    version: str = ""
    log_level: str = "INFO"
    run_local: bool = False

    root_path: str = sys.path[0]

    @field_validator("root_path")
    def validate_root_path(cls, value: str, info: ValidationInfo):
        # if run_local is true, return the raw value obtained for root_path
        if info.data["run_local"]:
            return value
        # if run_local is false, assume we are running in docker, and use '/app' as root_path
        # this preserves back-wards compatible behavior for initial songbird installations
        else:
            return os.path.join(os.sep, "app")

    data_path: str = "data"
    itunes_search_api_base_url: str = "https://itunes.apple.com/search"
    itunes_enabled: bool = True
    itunes_folder_path: Optional[str] = "itunesauto"
    itunes_lib_path: Optional[str] = "ituneslib"
    gdrive_enabled: bool = True
    gdrive_folder_path: Optional[str] = "gdrive"
    gdrive_folder_id: Optional[str] = ""
    gdrive_auth_port: int = 8080
    local_song_store_str: str = "dump"
    fname_dup_key: str = "_dup"
    fname_dup_limit: int = 8
    youtube_dl_enabled: bool = True
    youtube_render_timeout: int = 20
    youtube_render_wait: float = 0.2
    youtube_render_sleep: int = 1
    youtube_render_retries: int = 3
    youtube_home_url: str = "https://www.youtube.com"
    youtube_search_url: str = "https://www.youtube.com/results"
    youtube_search_tag: str = "search_query"
    youtube_searchform_payload: dict = {youtube_search_tag: ""}
    youtube_dl_retries: int = 3
    file_format: str = "mp3"

    class ConfigDict:
        env = os.getenv("ENV", "dev")
        config_path = os.path.join(os.path.dirname(sys.path[0]), f"{env}.env")
        env_file = config_path
        env_file_encoding = "utf-8"

    def get_data_path(self):
        return os.path.join(self.root_path, self.data_path)

    def get_local_folder_path(self):
        return os.path.join(self.get_data_path(), self.local_song_store_str)

    def get_itunes_folder_path(self) -> str:
        """If you run the app locally, configure the itunes path as an absolute path. Otherwise, the program will
        use the local container storage and assume to be running in a docker container.

        Returns:
            str: the path to where itunes destined songs should live
        """
        if self.run_local:
            return self.itunes_folder_path
        return os.path.join(self.get_data_path(), self.itunes_folder_path)

    def get_itunes_lib_path(self) -> str:
        """If you run the app locally, configure the itunes path as an absolute path. Otherwise, the program will
        use the local container storage and assume to be running in a docker container.

        Returns:
            str: the path to where itunes destined songs should live
        """
        if self.run_local:
            return self.itunes_lib_path
        return os.path.join(self.get_data_path(), self.itunes_lib_path)

    def get_gdrive_folder_path(self):
        return os.path.join(self.get_data_path(), self.gdrive_folder_path)


class SongbirdServerConfig(BaseSettings):
    """Configuration using .env file or defaults declared in here"""

    version: str = ""
    run_local: bool = False
    root_path: str = sys.path[0]

    class ConfigDict:
        config_path = os.path.join(os.path.dirname(sys.path[0]), ".env")
        env_file = config_path
        env_file_encoding = "utf-8"
