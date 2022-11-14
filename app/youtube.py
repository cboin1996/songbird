import logging
from typing import Optional
import web
from models import itunes_api
import requests_html
from bs4 import BeautifulSoup
import common
import os, sys

logger = logging.getLogger(__name__)
import yt_dlp as youtube_dl
from yt_dlp.utils import DownloadError, UnavailableVideoError, ExtractorError


def get_video_links(
    session: web.SimpleSession,
    youtube_home_url: str,
    youtube_search_url: str,
    youtube_query_payload: dict,
    render_timeout: int,
):

    # First, enter the search form on the youtube home page
    response = session.enter_search_form(
        search_url=youtube_search_url,
        payload=youtube_query_payload,
        render_timeout=render_timeout,
    )
    if response == None:
        logger.error(
            f"Error occurred performing a search for {youtube_query_payload} against url {youtube_search_url}. Please try again."
        )
        return None
    # Get the list of hrefs to each video on the home page
    links = response.html.find("#video-title")
    if len(links) == 0:
        logger.warn(
            f"Thats odd. Youtube gave me no videos for this search. Youll have to try something else: {youtube_query_payload}"
        )
        return
    link_list = []
    # create a user friendly list, containing videos with title and href refs.
    for idx, link in enumerate(links):
        if "title" in link.attrs and "href" in link.attrs:
            link_list.append(
                f"{link.attrs['title']} - {youtube_home_url+link.attrs['href']}"
            )
        # the actual raw list should match list size so we can properly select the link after.
        else:
            links.pop(idx)

    # Allow user to select the link they want to download
    common.pretty_lst_printer(link_list)

    video_selection_idx = common.select_items_from_list(
        "Select the song you wish to download!", link_list, 1, return_value=False
    )
    if len(video_selection_idx) == 0 or video_selection_idx is None:
        return None

    video_url = youtube_home_url + links[video_selection_idx[0]].attrs["href"]
    return video_url


class YtDlLogger(object):
    """
    Used for setting up youtube_dl logging
    """

    def info(self, msg):
        logger.info(msg)

    def debug(self, msg):
        logger.debug(msg)

    def warning(self, msg):
        logger.warning(msg)

    def error(self, msg):
        logger.error(msg)


def my_hook(d):
    """
    Hook for youtube_dl
    Args:
        d: download object from youtube_dl
    """
    if d["status"] == "finished":
        sys.stdout.write("\n")
        logger.info("Done downloading, now converting ...")

    if d["status"] == "downloading":
        p = d["_percent_str"]
        p = p.replace("%", "")
        song_name = d["filename"].split(os.sep)[-1]
        sys.stdout.write(
            f"\rDownloading to file: {song_name}, {d['_percent_str']}, {d['_eta_str']}"
        )
        sys.stdout.flush()
    if d["status"] == "error":
        logger.error("Error occured during download.")
        success_downloading = False


def run_download(url: str, file_path_no_format: str, file_format: str) -> str:
    """Run a download from youtube

    Args:
        url (str): the url to download
        file_path_no_format (str): the file path excluding file format
        file_format (str): the file format
    Returns:
        str: the filepath.
    """
    local_file_path = f"{file_path_no_format}.{file_format}"
    ydl_opts = {
        "format": "bestaudio/best",
        "cachedir": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": file_format,
                "preferredquality": "192",
            }
        ],
        "nocheckcertificate": True,
        "logger": YtDlLogger(),
        "progress_hooks": [my_hook],
        "outtmpl": file_path_no_format + ".%(ext)s",
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
        logger.info(f"Downloading successful. File stored locally: {local_file_path}")
        return local_file_path
    except Exception as e:
        logger.exception(f"Failed to complete the download of song at url: {url}.")
        return None


def run_download_process(
    session: web.SimpleSession,
    file_path_no_format: str,
    youtube_home_url: str,
    youtube_search_url: str,
    youtube_query_payload: dict,
    file_format: str,
    render_timeout: int,
) -> str:
    """Download a song from youtube.

    Args:
        file_name (str): the absolute path of where to save the file
        youtube_home_url (str): the url to youtube's home page
        youtube_search_url (str): the search url for youtube
        youtube_query_payload (str): the query payload for youtube's search api
        song_properties (itunes_api.ItunesApiSongModel): Optionally include song properties for a smarter search.

    Returns:
        str: the path on disk that the file was saved to. None if the download fails.
    """
    # obtain video selection from user
    video_url = get_video_links(
        session,
        youtube_home_url,
        youtube_search_url,
        youtube_query_payload,
        render_timeout,
    )
    if video_url is None:
        return
    # Process the download, and save locally
    return run_download(video_url, file_path_no_format, file_format)
