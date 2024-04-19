"""
helpers.py module for helping with parsing inputs
"""

from typing import Optional, List, Union, Any
from songbirdcore import common, itunes
from songbirdcore.models import modes, itunes_api
import logging

logger = logging.getLogger(__name__)


def launch_album_mode(
    artist_album_string="", quit_str="q"
) -> Optional[Union[List[itunes_api.ItunesApiSongModel], str]]:
    """launch album mode: collect album and songs to download

    Args:
        artist_album_string (str, optional): the string used when querying itunes api. Defaults to ''.
        quit_str (str, optional): the str to signify user quitting the process. Defaults to "q".

    Returns:
        Optional[Union[List[itunes_api.ItunesApiSongModel],str]]: the list of song properties gathered from the search, None if error occured, quit_str if user quit

    """
    while True:
        album_props = parse_itunes_search_api(
            search_variable=artist_album_string,
            mode=modes.Modes.ALBUM,
            lookup=False,
            # disable no selection here, user must select album properties.
            no_selection_value=None,
        )
        # check if user quit
        if album_props == quit_str:
            return quit_str

        if album_props is None:
            return None

        # get the song matching the album metadata
        songs_in_album_props = itunes.query_api(
            search_variable=album_props.collectionId,  # get list of songs for chosen album
            limit=album_props.trackCount,
            mode=modes.Modes.SONG,
            lookup=True,
        )
        # api error occurred
        if songs_in_album_props == None:
            return None
        # no songs found for album
        if len(songs_in_album_props) == 0:
            logger.error(
                "Sorry. Cant seem to find any details for this album in itunes api! Please select a different album."
            )
            return None

        songs_in_album_props = remove_songs_selected(
            song_properties_list=songs_in_album_props, quit_str=quit_str
        )
        if songs_in_album_props == quit_str:
            return quit_str
        if songs_in_album_props is None:
            return None

        return songs_in_album_props


# entity is usually song for searching songs
def parse_itunes_search_api(
    search_variable: str,
    mode: modes.Modes,
    limit: int = 20,
    lookup: bool = False,
    no_selection_value: Optional[int] = -1,
    quit_str: str = "q",
) -> Optional[
    Union[bool, itunes_api.ItunesApiSongModel, itunes_api.ItunesApiAlbumKeys]
]:
    """perform a query of the items api, allowing user to select
    an item from the returned list of options

    Args:
        search_variable (str): the value for the query
        mode (modes.Modes): the mode to run
        limit (int, optional): number of results. Defaults to 20.
        lookup (bool, optional): whether to enable 'lookup' mode in itunes api. Defaults to False.
        no_selection_value (int, optional): whether to set an option for 'no selection' from stdin
        quit_str (str, optional): str value used to determine whether to quit the song selection process

    Returns:
        Optional[Union[itunes_api.ItunesApiSongModel]]: returns the selected song properties, a bool=False if use continues without selection, None if error occurred, or quit_str if user quit.
    """
    parsed_results_list = itunes.query_api(search_variable, limit, mode, lookup=lookup)

    # Present results to user
    common.pretty_list_of_basemodel_printer(parsed_results_list)
    logger.info("Searched for: %s" % (search_variable))
    # Only one item can be selected
    user_selection = select_items_from_list(
        prompt="Select the number for the properties you want",
        lyst=parsed_results_list,
        n_choices=1,
        quit_str=quit_str,
        no_selection_value=no_selection_value,
    )

    # user has quit
    if user_selection == quit_str:
        logger.info("Quitting.")
        return quit_str
    if len(user_selection) == 0:
        logger.info("Continuing without properties.")
        return False

    print(f"Selected item: ")
    for k, v in user_selection[0].model_dump().items():
        print(" - %s : %s" % (k, v))

    return user_selection[0]


def remove_songs_selected(song_properties_list, quit_str: str = "q") -> Optional[List]:
    """Given a list of songs properties, allow the user to remove
    via stdio

    Args:
        song_properties_list (Any): the list of song properties

    Returns:
        Optional[List]: the properties list after selection
    """
    common.pretty_list_of_basemodel_printer(song_properties_list)
    input_string = "Enter song id's (1 4 5 etc.) you dont want from this album"
    user_input = select_items_from_list(
        input_string,
        song_properties_list,
        n_choices=len(song_properties_list) - 1,
        sep=" ",
        quit_str=quit_str,
        opposite=True,
        no_selection_value=-1,
    )
    # user has quit
    if user_input == quit_str:
        return quit_str
    if user_input == None:
        return None
    # user selects all songs
    if user_input == []:
        return song_properties_list
    # otherwise, user gets the processed list with their items removed
    return user_input


def get_input(
    prompt: str, out_type=None, quit_str="q", choices: Optional[List] = None
) -> Optional[Any]:
    """Given a prompt, get input from stdio and perform basic type validation

    Args:
        prompt (str): the prompt to use
        out_type (type, optional): expected type for input. Defaults to None.
        quit_str (str, optional): a character to signify quitting from the input gatherer. Defaults to "q".
        choices (Optional[List], optional): valid character options to parse as input. Defaults to None.

    Returns:
        Optional[Any]: the typed user input, None if error occured, quit_str if use quit
    """
    while True:
        built_prompt = prompt
        if choices is not None:
            built_prompt += f" , choices=({choices})"
        built_prompt += " ['q' quits]: "
        inp = input(built_prompt)
        if inp == quit_str:
            return quit_str

        # initialize type to be empty by default
        typed = None
        if out_type is not None:
            try:
                typed = out_type(inp)

            except ValueError as e:
                logger.error(
                    "Invalid type received. Try again, inputting an '{out_type}'"
                )
        else:
            typed = inp

        if choices is None:
            return typed

        if typed not in choices:
            logger.error(f"You must input one of {choices}")
        else:
            return typed


def get_input_list(prompt: str, sep: str, out_type=int, quit_str="q") -> List[int]:
    """Take an input prompt, and generate a typed list from it, validating against the given input type.

    Args:
        prompt (str): the prompt to display to the user
        sep (str): the expected separator in the input list
        out_type (_type_, optional): The expected data type. Defaults to int.

    Raises:
        ValueError: If the input does not match the given type.

    Returns:
        Optional[List[int]]: the typed list, or the quit_str value if user quits
    """
    while True:
        inp = input(prompt + f" ['{quit_str}' quits]: ")
        if inp == quit_str:
            return quit_str

        str_list = inp.split(sep)
        typed_list = []
        # by default fail type check
        type_check_passed = False
        for item in str_list:
            type_check_passed = True
            try:
                typed_inp = out_type(item)
            except ValueError as e:
                logger.error(
                    f"Invalid input {inp} recieved, expected list with types: {out_type}, separated by '{sep}'"
                )
                type_check_passed = False
                break

            typed_list.append(out_type(item))

        # only exit loop if the type check has passed
        if type_check_passed:
            break
    return typed_list


def select_items_from_list(
    prompt: str,
    lyst: List,
    n_choices: int,
    sep: Optional[str] = None,
    quit_str: str = "q",
    opposite: bool = False,
    no_selection_value: int = None,
    return_value: bool = True,
) -> List:
    """Input validation against a list.

    Args:
        prompt (str): prompt to display to user
        sep    (str): the separator for the input
        lyst (List): the list to perform input validation against
        n_choices (int): the number of choices allowed
        quit_str (str): The string to cancel validation and exit. Defaults to "q".
        opposite (bool): return everything BUT the user selection
        no_selection_value (int, optional): value to indicate no selection wanted from the user
        return_value (bool): if true, return the value, otherwise return the indicies of selections

    Returns:
        Optiona[List]: quit_str if user quits, [] if user selects nothing, otherwise a list of the users selections are returned.
    """
    tries = 0
    low = 0
    high = len(lyst) - 1
    # provide useful ranges to user
    if high == -1:
        range_display = ""
    elif high == 0:
        range_display = f" (choose {high})"
    else:
        range_display = f" (choose {low} to {high}) "
    # fill appropriate prompt based on opposite feature
    if opposite:
        opposite_prompt = " select all"
    else:
        opposite_prompt = " continue without selection"

    if no_selection_value is None:
        no_selection_prompt = ""
    else:
        no_selection_prompt = f"[{no_selection_value} {opposite_prompt}]"

    while True:
        tries += 1
        if tries > 5:
            logger.info(f"Wtf man. {tries} tries so far? Just get it right!")
        # get user input
        inp = get_input_list(
            prompt + f"{range_display} {no_selection_prompt}",
            sep,
            quit_str=quit_str,
            out_type=int,
        )
        if inp == quit_str:
            return quit_str

        if len(inp) == 0:
            logger.info("You selected nothing.")
            return []
        # verify if the value of the input is the selection value
        if inp[0] == no_selection_value:
            return []
        # if user has entered too many choices, try again!!
        if len(inp) > n_choices:
            logger.error(f"You're only allowed {n_choices} here. Try again.")
            continue
        # user has passed validation, now check the values are reasonable

        boundary_check_passed = True
        for val in inp:
            if val > high or val < low:
                logger.error(
                    f"Sorry, the value {val} is out of bounds. Please enter within the interval [{low}, {high}]"
                )
                boundary_check_passed = False
        if not boundary_check_passed:
            continue

        # if user gets passed all of above, actually select values or indices at this point, and return
        if not opposite:
            result = []
            for val in inp:
                if return_value:
                    result.append(lyst[val])
                else:
                    result.append(val)
        else:
            result = []
            for idx in range(len(lyst)):
                if idx not in inp:
                    if return_value:
                        result.append(lyst[idx])
                    else:
                        result.append(idx)
        return result
