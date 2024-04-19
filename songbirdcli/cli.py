import logging
import datetime
from enum import Enum
from typing import Optional, List, Union
import requests
import os, sys, shutil

from songbirdcli import settings
from songbirdcli import helpers
from songbirdcli import version

from songbirdcore.models import modes, itunes_api
from songbirdcore import itunes
from songbirdcore import youtube
from songbirdcore import gdrive
from songbirdcore import common

"""Entrypoint for songbirdcli. Run cli.py as a script to run songbirdcli.
See the README.md for configuration details.
"""

logger = logging.getLogger(__name__)


def validate_essentials(config: settings.SongbirdCliConfig) -> bool:
    """perform startup validation of the configuration,
    ensuring pre-conditions are met

    Args:
        config (settings.SongbirdCliConfig): the songbirdcli pydantic model

    Returns:
        bool: True if success, False otherwise
    """
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


def run_download_process(
    file_path_no_format: str,
    youtube_home_url: str,
    youtube_search_url: str,
    youtube_query_payload: dict,
    file_format: str,
    render_timeout: int,
    render_wait: float,
    render_retries: int,
    render_sleep: int,
    quit_str: str = "q",
) -> str:
    """Download a song from youtube.

    Args:
        file_path_no_format (str): the absolute path of where to save the file (excluding file format)
        youtube_home_url (str): the url to youtube's home page
        youtube_search_url (str): the search url for youtube
        youtube_query_payload (str): the query payload for youtube's search api
        file_format (str): desired file format
        render_timeout (int): amount of time before abandoning a render
        render_wait (float): the amount of time before attempting a render
        render_retries (int): the number of retries for a render
        render_sleep (int): the amount of time to wait after rendering

    Returns:
        str: the path on disk that the file was saved to, None if failure occured, quit_str if user quit
    """
    is_valid_url = False
    while not is_valid_url:
        # obtain video selection from user
        video_url = helpers.get_input(
            prompt=f"Enter a URL, or hit enter to use '{youtube_query_payload}' as a query to youtube: ",
            out_type=str,
            quit_str=quit_str,
        )
        # if user hits enter, bypass url checks
        if video_url == "":
            break

        if video_url == quit_str:
            return quit_str

        if video_url is None:
            return None
        try:
            response = requests.get(video_url)
        except Exception as e:
            logger.error(f"exception occured testing your url: {e}")
            continue

        # only continue if url was valid
        if response.status_code == 200:
            is_valid_url = True
        else:
            logger.error(
                f"URL is valid, but could not receive 200 status from {video_url}, is internet down?"
            )

        # empty str (enter) query youtube
    if video_url == "":
        link_list, links = youtube.get_video_links(
            youtube_home_url,
            youtube_search_url,
            youtube_query_payload,
            render_timeout,
            render_wait,
            render_retries,
            render_sleep,
        )

        if link_list is None:
            return

        # Allow user to select the link they want to download
        common.pretty_lst_printer(link_list)

        video_selection_idx = helpers.select_items_from_list(
            "Select the song you wish to download!",
            link_list,
            1,
            return_value=False,
        )
        if video_selection_idx == quit_str:
            return quit_str

        if video_selection_idx is None or len(video_selection_idx) == 0:
            return None

        video_url = youtube_home_url + links[video_selection_idx[0]].attrs["href"]
    # Process the download, and save locally
    return youtube.run_download(video_url, file_path_no_format, file_format)


def run_for_song(
    config: settings.SongbirdCliConfig,
    song_name: str,
    song_properties: Optional[itunes_api.ItunesApiSongModel],
    quit_str: str = "q",
) -> Union[bool, None, str]:
    """Run a cycle of the application given a song.

    Args:
        config (settings.SongbirdConfig): the songbird config
        song_name (str): the name of the song to run the app for
        song_properties (Optional[itunes_api.ItunesApiSongModel]): optionally include song properties. Including these skips the itunes api parser.

    Returns:
        Union[bool, None, str]: returns boolean indicating success/failure. None indicated error occurred, quit_str indicates user quit
    """
    logger.info(f"Searching for: {song_name}")
    file_itunes = []
    file_gdrive = []
    # itunes craves m4a formatted files. Otherwise we use mp3s, as were civilized people.
    file_format = config.file_format if not config.itunes_enabled else "m4a"
    # check if song exists locally in dump folder
    file_local = common.find_file(config.get_local_folder_path(), f"*{song_name}*")
    # check if song exists locally in itunes
    if config.itunes_enabled:
        file_itunes = itunes.itunes_lib_search(config.get_itunes_lib_path(), song_name)
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
        inp = helpers.get_input(
            "Do you want to proceed with download anyway?", choices=["y", "n"]
        )
        # user quits or selects no
        if inp == quit_str or inp == "n":
            return quit_str

        if inp is None:
            return

    if song_properties is None:
        song_properties = helpers.parse_itunes_search_api(song_name, modes.Modes.SONG)

    if song_properties == quit_str:
        return quit_str

    file_path_no_format = os.path.join(config.get_local_folder_path(), song_name)
    file_path = file_path_no_format + "." + file_format
    downloaded_file_path = None
    # make sure file doesnt already exist
    duped_filepath = common.fname_duper(file_path, config.fname_dup_limit, 1, "_dup")
    if duped_filepath is None:
        return
    if duped_filepath != file_path:
        logger.warning(
            f"Duplicate file(s) already exist for base file {file_path}, so I generated a new filename {duped_filepath}!"
        )
        file_path_no_format = os.path.splitext(duped_filepath)[0]
        file_path = duped_filepath
    # run the youtube downloader
    if config.youtube_dl_enabled:
        payload = config.youtube_searchform_payload
        # if song_properties is False, user selected no properties
        if song_properties != False:
            payload[config.youtube_search_tag] = (
                f"{song_properties.artistName} {song_properties.trackName}"
            )
        else:
            payload[config.youtube_search_tag] = song_name

        downloaded_file_path = run_download_process(
            file_path_no_format=file_path_no_format,
            youtube_home_url=config.youtube_home_url,
            youtube_search_url=config.youtube_search_url,
            youtube_query_payload=payload,
            file_format=file_format,
            render_timeout=config.youtube_render_timeout,
            render_wait=config.youtube_render_wait,
            render_retries=config.youtube_render_retries,
            render_sleep=config.youtube_render_sleep,
            quit_str=quit_str,
        )
    if downloaded_file_path == quit_str:
        return quit_str

    if downloaded_file_path is None:
        return

    # perform sanity check in case no file exists and yt-dlp didnt throw an error
    if not os.path.exists(downloaded_file_path):
        logger.error(
            f"yt-dlp reported no error downloading file, but file does not exist. Cannot proceed with tagging as no file exists."
        )
        return

    if song_properties != False:
        # tag file if user specified song properties
        tag_successful = False
        if file_format == "mp3":
            tag_successful = itunes.mp3ID3Tagger(downloaded_file_path, song_properties)
        elif file_format == "m4a":
            tag_successful = itunes.m4a_tagger(downloaded_file_path, song_properties)
        else:
            logger.warning(
                "You've specified a file format that is has no tagger supported yet. Saving file without tags."
            )

    # provide user with choices for where to save their file to.
    save_prompt_base = "Would you like to save your file to"
    if config.itunes_enabled and config.gdrive_enabled:
        inp = helpers.get_input(
            save_prompt_base + " gdrive (g), itunes (i), or locally (l)",
            out_type=str,
            choices=["g", "i", "l"],
        )

    if config.itunes_enabled and not config.gdrive_enabled:
        inp = helpers.get_input(
            save_prompt_base + " itunes (i), or locally (l)",
            out_type=str,
            choices=["i", "l"],
        )

    if not config.itunes_enabled and config.gdrive_enabled:
        inp = helpers.get_input(
            save_prompt_base + " gdrive (g), or locally (l)",
            out_type=str,
            choices=["g", "l"],
        )

    if not config.itunes_enabled and not config.gdrive_enabled:
        inp = "l"

    if inp == quit_str:
        return quit_str
    if inp is None:
        return

    if inp == "i":
        msg = "Saved to itunes"
        itunes_dest_path = common.fname_duper(
            os.path.join(
                config.get_itunes_folder_path(), os.path.basename(downloaded_file_path)
            ),
            config.fname_dup_limit,
            1,
            config.fname_dup_key,
        )
        if itunes_dest_path is None:
            return None
        shutil.move(downloaded_file_path, itunes_dest_path)
    elif inp == "g":
        msg = "Saved to gdrive"
        gdrive_dest_path = common.fname_duper(
            os.path.join(
                config.get_gdrive_folder_path(), os.path.basename(downloaded_file_path)
            ),
            config.fname_dup_limit,
            1,
            config.fname_dup_key,
        )
        if gdrive_dest_path is None:
            return None
        shutil.move(downloaded_file_path, gdrive_dest_path)
        # If running in a container, we need to provide a bind address
        # Users are expected to run the container with hostname songbird (--hostname songbird)
        bind_addr = None
        if not config.run_local:
            bind_addr = "songbird"
        gdrive.save_song(
            config.gdrive_folder_id,
            credentials_path=os.path.join(
                config.get_gdrive_folder_path(), "credentials.json"
            ),
            token_path=os.path.join(config.get_gdrive_folder_path(), "token.json"),
            song_name=f"{song_name}.{file_format}",
            song_path=str(gdrive_dest_path),
            auth_port=config.gdrive_auth_port,
            bind_addr=bind_addr,
        )
    else:
        msg = "Saved locally."

    logger.info(msg)
    return True


def get_songs_from_user(
    current_mode: modes.Modes, quit_str: str = "q"
) -> Optional[Union[str, List[str]]]:
    # launch album mode to collect songs
    if current_mode == modes.Modes.ALBUM:
        album_name = helpers.get_input(
            f"Enter an album name.", out_type=str, quit_str=quit_str
        )
        # quit condition
        if album_name == quit_str:
            return quit_str
        if album_name is None:
            return None

        mode = resolve_mode(album_name, current_mode=current_mode)
        # detect mode change and return to main menu
        if mode is not None:
            return mode

        album_song_properties = helpers.launch_album_mode(album_name)
        # quit iteration to main menu
        if album_song_properties == quit_str:
            return quit_str
        if album_song_properties is None:
            return None
        return [song.trackName for song in album_song_properties]

    # launch song mode to collect songs
    elif current_mode == modes.Modes.SONG:
        songs = helpers.get_input_list(
            "Please input song(s), separated by ';'. E.g. song1; song2; song3.",
            out_type=str,
            sep="; ",
        )
        # quit iteration to main menu
        if songs == quit_str:
            return quit_str
        if songs is None:
            return None

        mode = resolve_mode(songs[0], current_mode=current_mode)
        # detect mode change and return to main menu
        if mode is not None:
            return mode
        return songs


def run(config: settings.SongbirdCliConfig):
    """main entrypoint for songbirdcli. Expects the songbirdcli config object.

    Args:
        config (settings.SongbirdCliConfig): songbirdcli settings pydantic model

    """
    # setup quit str for user
    quit_str = "q"
    try:
        common.set_logger_config_globally(log_level=config.log_level)
        common.name_plate(entries=[f"--cli {config.version}"])
        # only need folders on OS if we are running locally. Otherwise user is expected to provied folders
        # via bind mounts
        if config.run_local:
            initialize_dirs(
                [
                    config.get_data_path(),
                    config.get_itunes_folder_path(),
                    config.get_itunes_lib_path(),
                    config.get_gdrive_folder_path(),
                    config.get_local_folder_path(),
                ]
            )
        if not validate_essentials(config):
            return None
        current_mode = modes.Modes.SONG
        while True:
            logger.info(f"---Songbird Main Menu v{config.version}🐦---")

            song_properties = None
            album_song_properties = None
            result = get_songs_from_user(current_mode=current_mode, quit_str=quit_str)
            # user quits
            if result == quit_str:
                return_to_menu = helpers.get_input(
                    prompt=f"Are you sure you want to quit?",
                    choices=["y", "n"],
                    out_type=str,
                    quit_str=quit_str,
                )
                # allow user to return to main menu before
                # full shutdown
                if return_to_menu == "n":
                    continue

                return quit_str

            # user changed mode
            if isinstance(result, modes.Modes):
                current_mode = result
                continue

            # error occurred
            if result is None:
                continue
            # set songs to result and continue otherwise
            songs = result
            logger.info(f"Searching for songs: {songs}")
            for i, song in enumerate(songs):
                if album_song_properties is not None:
                    song_properties = album_song_properties[i]
                success = run_for_song(config, song, song_properties, quit_str)

                # detect if more songs are queued, and asks if user wants to continue with other songs
                if (success == quit_str or success == None) and i + 1 < len(songs):
                    songs_remaining = songs[i + 1 :]
                    common.pretty_lst_printer(songs_remaining)
                    return_to_menu = helpers.get_input(
                        prompt=f"You have {len(songs_remaining)} songs (above) in queue. Would you like to continue?",
                        choices=["y", "n"],
                        out_type=str,
                        quit_str=quit_str,
                    )
                    # only return to main menu if user opts to, otherwise enter next iteration
                    # to preserve list of selections
                    if return_to_menu == "n" or return_to_menu == quit_str:
                        break
                    if return_to_menu == "y":
                        continue

    except KeyboardInterrupt as e:
        logger.info("\nReceived keyboard interrupt :o")

    logger.info("Shutting down!")


if __name__ == "__main__":
    config = settings.SongbirdCliConfig(version=version.version)
    run(config=config)
