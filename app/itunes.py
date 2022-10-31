from typing import List, Optional

from config import settings


def itunes_lib_search(
    config: settings.SongbirdConfig,
    song_paths: List,
    search_parameters="",
    album_properties=None,
):
    """
    Performs a search on users iTunes library by album, artist and genre
    Args:
        song_paths: paths to all iTunes songs
        search_parameters: search term
        album_properties: determines whether to do a smarter search based on given album properties
    Returns
    """
    song_paths = []
    for song_path in song_paths:
        song_name_split = song_path.split(os.sep)
        song_name = youtube.remove_illegal_characters(
            song_name_split[len(song_name_split) - 1].lower()
        )
        album_name = youtube.remove_illegal_characters(
            song_name_split[len(song_name_split) - 2].lower()
        )
        artist_name = youtube.remove_illegal_characters(
            song_name_split[len(song_name_split) - 3].lower()
        )
        search_parameters = youtube.remove_illegal_characters(search_parameters.lower())
        if album_properties == None:
            formatted_song_name = song_name + " " + album_name + " " + artist_name
            # songNameSplit is list of itunes file path.. artist is -3 from length, song is -1
            if search_parameters in formatted_song_name:
                song_paths.append(song_path)
        else:
            if (
                album_properties[config.itunes_api_keys.track_name].lower()
                in artist_name
                and search_parameters in song_name
            ):
                song_paths.append(song_path)
    return song_paths.sort()
