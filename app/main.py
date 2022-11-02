import logging
import datetime
from enum import Enum
from typing import Optional

import common
from config import settings
from models import modes, itunes_api
import itunes

logger = logging.getLogger(__name__)


def mode_select(valid_modes=modes.Modes, quit_str="q") -> Optional[modes.Modes]:
    mode = common.get_input_list("Please input song(s), separated by ';'. E.g. song1; song2; song3. To initiate album mode, type 'alb'", out_type=str, sep="; ")
    if mode is None:
        return
    try:
        return modes.Modes(mode[0])

    except ValueError:
        logger.info(f"Initiating download sequence for: {mode}")

    return mode

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
    yt_links = run_song_selector()

def run(config: settings.SongbirdConfig):
    common.set_logger_config_globally(timestamp=datetime.datetime.now())
    print(common.name_plate())
    while True:
        # select app mode
        mode_or_songs = mode_select()
        album_song_properties = None
        # none type mode indicates user has quit.
        if mode_or_songs is None:
           return

        # launch album mode to collect songs
        if mode_or_songs == modes.Modes.ALBUM:
            # TODO: implement
            album_name = common.get_input("Enter an album name", out_type=str)
            album_song_properties = itunes.launch_album_mode(album_name)
            songs = [song.trackName for song in songs_in_album_props]

        # by default, use songs provided in mode selection
        else:
            songs = mode_or_songs

        logger.info(f"Searching for songs: {songs}")
        for song in songs:
            run_for_song(config, song, album_song_properties)

    logger.info("Shutting down!")

if __name__ == "__main__":
    run(config=settings.SongbirdConfig())
