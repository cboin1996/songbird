import logging
import datetime
from enum import Enum
from typing import Optional, List
import os
import common
from config import settings
from models import modes, itunes_api
import itunes
import youtube
import gdrive
import web
import shutil

logger = logging.getLogger(__name__)


def validate_essentials(config: settings.SongbirdConfig):
    success = True
    if config.gdrive_enabled:
        if not os.path.exists(config.get_gdrive_folder_path()):
            logger.error(
                f"You must create the path {config.get_gdrive_folder_path()} \
             to use google drive feature! If using docker, use bind mounts. See README for more info."
            )
            success = False
        if not os.path.exists(
            os.path.join(config.get_gdrive_folder_path(), "credentials.json")
        ):
            logger.error(
                f"You must provide a credentials.json file inside of {config.get_gdrive_folder_path()} to use gdrive feature!"
            )
            success = False

    if config.itunes_enabled:
        if not os.path.exists(config.get_itunes_folder_path()):
            logger.error(
                f"You must create the path {config.get_itunes_folder_path()} \
             to use itunes feature! If using docker, use bind mounts. See README for more info."
            )
            success = False

        if not os.path.exists(config.get_itunes_lib_path()):
            logger.error(
                f"You must create the path {config.get_itunes_lib_path()} \
             to use itunes feature! If using docker, use bind mounts. See README for more info."
            )
            success = False

    if not os.path.exists(config.get_data_path()):
        logger.error(
            f"At minimum, you need path {config.get_data_path()} configured to run the app. If using docker, use bind mounts. See README."
        )
    return success


def initialize_dirs(dirs: List[str]):
    """Initialize the apps directories

    Args:
        dirs (List[str]): the list of directories to initialize (create)
    """
    for _dir in dirs:
        if not os.path.exists(_dir):
            logger.info(f"Creating dir: {_dir}")
            os.mkdir(_dir)


def resolve_mode(
    inp: str, current_mode: modes.Modes = modes.Modes.SONG
) -> Optional[modes.Modes]:
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


def run_for_song(
    config: settings.SongbirdConfig,
    song_name: str,
    song_properties: Optional[itunes_api.ItunesApiSongModel],
    session: Optional[web.SimpleSession],
):
    """Run a cycle of the application given a song.

    Args:
        config (settings.SongbirdConfig): the songbird config
        song_name (str): the name of the song to run the app for
        song_properties (Optional[itunes_api.ItunesApiSongModel]): optionally include song properties. Including these skips the itunes api parser.
    """
    logger.info(f"Searching for: {song_name}")
    file_itunes = []
    file_gdrive = []
    # itunes craves m4a formatted files. Otherwise we use mp3s, as were civilized people.
    file_format = "mp3" if not config.itunes_enabled else "m4a"
    # check if song exists locally in dump folder
    file_local = common.find_file(config.get_local_folder_path(), f"*{song_name}*")
    # check if song exists locally in itunes
    if config.itunes_enabled:
        file_itunes = itunes.itunes_lib_search(config.itunes_lib_path, song_name)
    # check if song exists locally in google drive folder
    if config.gdrive_enabled:
        file_gdrive = common.find_file(
            config.get_gdrive_folder_path(), f"*{song_name}*"
        )
    # if any of the above, ask user if they want to download anyways
    files = file_local + file_itunes + file_gdrive
    if len(files) > 0:
        logger.info("Found the following similar files:")
        common.pretty_lst_printer(files)
        inp = common.get_input(
            "Do you want to proceed with download anyway?", choices=["y", "n"]
        )

        if inp == "q" or inp == "n":
            return

    if song_properties is None:
        song_properties = itunes.parse_itunes_search_api(song_name, modes.Modes.SONG)

    if song_properties is None:
        return
    file_path_no_format = os.path.join(config.get_local_folder_path(), song_name)
    file_path = file_path_no_format + "." + file_format
    downloaded_file_path = None
    # make sure file doesnt already exist
    if os.path.exists(file_path):
        logger.warning(f"Duplicate file found: {file_path}")
        file_path_no_format += "_dup"
        file_path = f"{file_path_no_format}.{file_format}"
        logger.warning(f"Renamed this dl to {file_path}")
    # run the youtube downloader
    if config.youtube_dl_enabled:
        payload = config.youtube_searchform_payload
        if song_properties != []:
            payload[
                config.youtube_search_tag
            ] = f"{song_properties.artistName} {song_properties.trackName}"
        else:
            payload[config.youtube_search_tag] = song_name

        downloaded_file_path = youtube.run_download_process(
            session=session,
            file_path_no_format=file_path_no_format,
            youtube_home_url=config.youtube_home_url,
            youtube_search_url=config.youtube_search_url,
            youtube_query_payload=payload,
            file_format=file_format,
            render_timeout=config.youtube_render_timeout,
        )

    if downloaded_file_path is None:
        return
    # tag file
    tag_successful = False
    if file_format == "mp3":
        tag_successful = itunes.mp3ID3Tagger(downloaded_file_path, song_properties)
    elif file_format == "m4a":
        tag_successful = itunes.m4a_tagger(downloaded_file_path, song_properties)
    else:
        logger.warn(
            "You've specified a file format that is has no tagger supported yet. Saving file without tags."
        )

    # provide user with choices for where to save their file to.
    save_prompt_base = "Would you like to save your file to"
    if config.itunes_enabled and config.gdrive_enabled:
        inp = common.get_input(
            save_prompt_base + " gdrive (g), itunes (i), or locally (l)",
            out_type=str,
            choices=["g", "i", "l"],
        )

    if config.itunes_enabled and not config.gdrive_enabled:
        inp = common.get_input(
            save_prompt_base + " itunes (i), or locally (l)",
            out_type=str,
            choices=["i", "l"],
        )

    if not config.itunes_enabled and config.gdrive_enabled:
        inp = common.get_input(
            save_prompt_base + " gdrive (g), or locally (l)",
            out_type=str,
            choices=["g", "l"],
        )

    if not config.itunes_enabled and not config.gdrive_enabled:
        inp = "l"

    if inp is None:
        return

    if inp == "i":
        msg = "Saved to itunes"
        shutil.move(downloaded_file_path, config.get_itunes_folder_path())
    elif inp == "g":
        msg = "Saved to gdrive"
        path = shutil.move(downloaded_file_path, config.get_gdrive_folder_path())
        gdrive.save_song(
            config.gdrive_folder_id,
            credentials_path=os.path.join(
                config.get_gdrive_folder_path(), "credentials.json"
            ),
            token_path=os.path.join(config.get_gdrive_folder_path(), "token.json"),
            song_name=song_name,
            song_path=str(path),
            auth_port=config.gdrive_auth_port,
        )
    else:
        msg = "Saved locally."

    logger.info(msg)


def run(config: settings.SongbirdConfig):
    try:
        common.set_logger_config_globally()
        common.name_plate()
        # only need folders on OS if we are running locally. Otherwise user is expected to provied folders
        # via bind mounts
        if config.run_local:
            initialize_dirs(
                [
                    config.get_data_path(),
                    config.get_itunes_folder_path(),
                    config.get_gdrive_folder_path(),
                    config.get_local_folder_path(),
                ]
            )
        if not validate_essentials(config):
            return None
        current_mode = modes.Modes.SONG
        session = None
        while True:
            if config.youtube_dl_enabled:
                if session is None:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
                        "Referer": "https://www.youtube.com/",
                        "Accept": "image/avif,image/webp,*/*",
                        "Host": "www.google.com",
                    }
                    session = web.SimpleSession(
                        "youtube", root_url=config.youtube_home_url, headers=headers
                    )

            logger.info("---Songbird Main Menu---")
            song_properties = None
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
                songs = common.get_input_list(
                    "Please input song(s), separated by ';'. E.g. song1; song2; song3.",
                    out_type=str,
                    sep="; ",
                )
                # quit condition
                if songs is None:
                    break
                mode = resolve_mode(songs[0], current_mode=current_mode)
                # detect mode change and return to main menu
                if mode is not None:
                    current_mode = mode
                    continue

            logger.info(f"Searching for songs: {songs}")
            for i, song in enumerate(songs):
                if album_song_properties is not None:
                    song_properties = album_song_properties[i]
                success = run_for_song(config, song, song_properties, session)
    except KeyboardInterrupt as e:
        logger.info("\nReceived keyboard interrupt :o")

    logger.info("Shutting down!")
    session.close()


if __name__ == "__main__":
    run(config=settings.SongbirdConfig())
