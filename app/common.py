from typing import List
import logging
import glob
import os

from models import itunes_api, modes
from typing import Optional
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)


def set_logger_config_globally(log_level=logging.INFO) -> None:
    """Sets the python logging module settings for output
    to stdout and to file.
    Args:
        timestamp (str): the timestamp to name the log file.
    """
    logging.basicConfig(
        level=log_level,
        format="[%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )


def name_plate():
    """
    Produces the application nameplate.
    Args: two command line argumates, debug mode on or off, operating system
    Returns: operating system
    """
    print("===============================")
    print("=-----Welcome to songbird-----=")
    print("===============================")
    print(
        f"At the main menu, type of of {[mode.value for mode in modes.Modes]} to switch modes!"
    )


def fname_duper(fname: str, limit: int, count: int, dup_key: str):
    """Generates a duplicate filename for when a filename already exists

    Args:
        fname (str): filename
        limit (int): a limit of dups before quitting the attempt
        count (int): recursive count tracker
        dup_key (str): the key to use as the duplicate addon

    Returns:
        Optional[str]: the modified filename, or None if the limit has been reached.
    """
    fname_split = os.path.splitext(fname)
    fname_noext = fname_split[0]
    ext = fname_split[1]
    if count == limit:
        logger.error(
            f"Max retry limit {limit} reached for fname {fname}. Please try changing some filenames and try again later."
        )
        return None
    if os.path.exists(fname):
        fname = fname_duper(fname_noext + dup_key + ext, limit, count + 1, dup_key)

    return fname


def get_input(prompt: str, out_type=None, quit_str="q", choices: Optional[List] = None):
    while True:
        built_prompt = prompt
        if choices is not None:
            built_prompt += f" , choices=({choices})"
        built_prompt += " ['q' quits]: "
        inp = input(built_prompt)
        if inp == quit_str:
            return None

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
        Optional[List[int]]: the typed list, or None if user quit
    """
    while True:
        inp = input(prompt + " ['q' quits]: ")
        if inp == quit_str:
            return None

        str_list = inp.split(sep)
        typed_list = []
        for item in str_list:
            type_check_passed = True
            try:
                typed_inp = out_type(item)
            except ValueError as e:
                logger.error(
                    f"Invalid input {inp} recieved, expected list with types: {out_type}, separated by '{sep}'"
                )
                type_check_passed = False
            if not type_check_passed:
                continue

            typed_list.append(out_type(item))
        return typed_list


def remove_illegal_characters(filename):
    """
    Used for stripping file names of illegal characters used for saving
    Args:
        filename(str): the file's name to strip
    Returns: stipped file name
    """
    return (
        filename.replace("\\", "")
        .replace('"', "")
        .replace("/", "")
        .replace("*", "")
        .replace("?", "")
        .replace("<", "")
        .replace(">", "")
        .replace("|", "")
        .replace("'", "")
        .replace(":", "")
    )


def find_file(path: str, filename: str) -> List[str]:
    """Simple glob search for a file

    Args:
        path (str): the path to the root folder to search within
        filename (str): the filename (supports glob patterns)

    Returns:
        List[str]: list of paths found that match
    """
    paths = glob.glob(os.path.join(path, filename))
    return paths


def pretty_list_of_basemodel_printer(list_of_dicts: List[BaseModel], ignore_keys=None):
    """
    prints list from top down so its more user friendly, items are pretty big
    params:
        list_of_dicts: list of dictionaries to print
        ignore_keys: any keys not to print
    """
    i = len(list_of_dicts) - 1
    logger.info("------------------------")
    for element in reversed(list_of_dicts):
        logger.info(i)
        for k, v in element.dict().items():
            if ignore_keys is not None:
                if (
                    k not in ignore_keys
                ):  # print the key and value if not in ignore_keys or special_dict
                    print("\t%s - %s" % (k, v))

            else:  # (default case) print the key and value
                print("\t%s - %s" % (k, v))
        i -= 1
        print("------------------------")


def pretty_lst_printer(lyst: List):
    for idx, item in enumerate(lyst):
        logger.info(f"\t [{idx}] - {item}")


def select_items_from_list(
    prompt: str,
    lyst: List,
    n_choices: int,
    sep: Optional[str] = None,
    quit_str: str = "q",
    opposite: bool = False,
    no_selection_value=-1,
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
        no_selection_value (any): value to indicate no selection wanted from the user
        return_value (bool): if true, return the value, otherwise return the indicies of selections
    Returns Optiona[List]: None if user quits, [] if user selects nothing, otherwise a list of the users selections are returned.
    """
    tries = 0
    low = 0
    high = len(lyst) - 1
    # provide useful ranges to user
    if high == 0:
        range_display = ""
    elif high == 1:
        range_display = f" (choose {high})"
    else:
        range_display = f" (choose {low} to {high}) "
    # fill appropriate prompt based on opposite feature
    if opposite:
        opposite_prompt = " select all"
    else:
        opposite_prompt = " continue without selection"

    while True:
        tries += 1
        if tries > 5:
            logger.info(f"Wtf man. {tries} tries so far? Just get it right!")
        # get user input
        inp = get_input_list(
            prompt + f"{range_display}[{no_selection_value} {opposite_prompt}]",
            sep,
            out_type=int,
        )
        if inp is None:
            return None
        print(inp)
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
