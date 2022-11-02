import logging
import datetime
from enum import Enum
from typing import Optional

import common
from config import settings
from models import modes, itunes_api
import itunes
import youtube

logger = logging.getLogger(__name__)


def resolve_mode(inp: str, current_mode: modes.Modes = modes.Modes.SONG) -> Optional[modes.Modes]:
    """Resolve the mode based on a given mode, against the current mode

    Args:
        inp (str): user input
        current_mode (modes.Modes, optional): The current mode of the app. Defaults to modes.Modes.SONG.

    Returns:
        Optional[modes.Modes]: return the mode if the current mode needs to be changed, otherwise return nothing.
    """
    try:
        mode = modes.Modes(inp)
        if mode != current_mode:
            logger.info(f"Switched to {mode.value} mode!")
            return mode
        else:
            return None
    except ValueError:
        return None

def run_for_song(config: settings.SongbirdConfig, song_name: str, song_properties: Optional[itunes_api.ItunesApiSongModel]):
    """Run a cycle of the application given a song.

    Args:
        config (settings.SongbirdConfig): the songbird config
        song_name (str): the name of the song to run the app for
        song_properties (Optional[itunes_api.ItunesApiSongModel]): optionally include song properties. Including these skips the itunes api parser.
    """
    logger.info(f"Searching for: {song_name}")
    file_itunes = []
    file_gdrive = []
    # check if song exists locally in dump folder
    file_local = common.find_file(config.get_local_folder_path(), f"*{song_name}*")
    # check if song exists locally in itunes
    if config.itunes_enabled:
        file_itunes = itunes.itunes_lib_search(config.itunes_lib_path, song_name)
    # check if song exists locally in google drive folder
    if config.gdrive_enabled:
        file_gdrive = common.find_file(config.get_gdrive_folder_path(), f"*{song_name}*")
    # if any of the above, ask user if they want to download anyways
    files = file_local + file_itunes + file_gdrive
    if len(file_local) > 0:
        logger.info("Found the following similar files:")
        common.pretty_lst_printer(files)
        inp = common.get_input("Do you want to proceed with download anyway?", choices=["y", "n"])

        if inp == "q" or "n":
            return

    if song_properties is None:
        song_properties = itunes.parse_itunes_search_api(song_name, modes.Modes.SONG)

    # TODO: Implement downloading a song.
    yt_links = youtube.get_youtube_song_list()

def run(config: settings.SongbirdConfig):
    common.set_logger_config_globally()
    common.name_plate()
    current_mode = modes.Modes.SONG
    while True:
        logger.info("---Songbird Main Menu---")
        album_song_properties = None

        # launch album mode to collect songs
        if current_mode == modes.Modes.ALBUM:
            album_name = common.get_input(f"Enter an album name.", out_type=str)
            # quit condition
            if album_name is None:
                break
            mode = resolve_mode(album_name, current_mode=current_mode)
            # detect mode change and return to main menu
            if mode is not None:
                current_mode = mode
                continue

            album_song_properties = itunes.launch_album_mode(album_name)
            songs = [song.trackName for song in album_song_properties]
        elif current_mode == modes.Modes.SONG:
            songs = common.get_input_list("Please input song(s), separated by ';'. E.g. song1; song2; song3.", out_type=str, sep="; ")
            # quit condition
            if songs is None:
                break
            mode = resolve_mode(songs[0], current_mode=current_mode)
            # detect mode change and return to main menu
            if mode is not None:
                current_mode = mode
                continue

        logger.info(f"Searching for songs: {songs}")
        for song in songs:
            run_for_song(config, song, album_song_properties)

    logger.info("Shutting down!")

if __name__ == "__main__":
    run(config=settings.SongbirdConfig())
