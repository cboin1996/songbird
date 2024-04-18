import pytest
from typing import List, Optional
from songbirdcli import helpers
from songbirdcore.models import modes
from songbirdcore import itunes

@pytest.fixture()
def parse_itunes_search_api(monkeypatch):
    return itunes.query_api(
        "jolene",
        mode=modes.Modes.SONG,
        limit=10
    )

@pytest.mark.parametrize(
    "query,input_sequence",
    (
        # get billy joel the stranger, and remove the first three songs
        ("the stranger billy joel", ["0", "1 2 3"]),
        # same as above, but specify no selection
        ("the stranger billy joel", ["0", "-1"]),
        # same as above, but quit
        ("the stranger billy joel", ["0", "q"])
    )
)
def test_launch_album_mode(monkeypatch, query, input_sequence):
    monkeypatch.setattr("builtins.input", lambda _: next(iter(input_sequence)))
    result = helpers.launch_album_mode(artist_album_string=query)


@pytest.mark.parametrize(
    "inp,out_type,choices,expected",
    [
        # ok with number casting to string
        (0, str, None, "0"),
        ("q", str, ["y", "n"], None),
        ("y", str, ["y", "n"], "y"),
        ("", str, None, ""),
        (0, int, [0, 1], 0),
        (2, int, None, 2),
        ("q", int, None, None),
    ],
)
def test_get_input(monkeypatch, inp, out_type, choices, expected):
    """test get_input() function"""
    # simulate user entering invalid inputs, and then one of the choices
    monkeypatch.setattr("builtins.input", lambda _: inp)
    output = helpers.get_input(
        "hello", out_type=out_type, quit_str="q", choices=choices
    )
    assert output == expected


@pytest.mark.parametrize(
    "out_type,quit_str,inp,expected",
    [
        (str,"q","hi;there",["hi","there"]),
        (int,"q","q",None),
    ]
)
def test_get_input_list(monkeypatch, out_type, quit_str: str, inp: str, expected):
    monkeypatch.setattr("builtins.input", lambda _: "q")

    inputs = helpers.get_input_list(prompt="hello", sep=";", out_type=str, quit_str="q")

    assert inputs == None


@pytest.mark.parametrize(
    "lyst,n_choices,opposite,no_selection_value,return_value,inp,expected",
    [
        (["option1", "option2"], 2, False, None, True, "0;1", ["option1", "option2"]),
        # same as above, but with opposite enabled
        (["option1", "option2"], 2, True, None, True, "0;1",  []),
        # same as above, but user uses -1 to quit
        (["option1", "option2"], 2, False, -1, True, "-1", []),
    ]
)
def test_select_items_from_list(
    monkeypatch,
    lyst: List,
    n_choices: int,
    opposite: Optional[bool],
    no_selection_value,
    return_value: Optional[bool],
    inp,
    expected
):
    """parametrized tester for select_items_from_list()"""
    monkeypatch.setattr("builtins.input", lambda _: inp)

    results = helpers.select_items_from_list(
        "hi",
        lyst=lyst,
        n_choices=n_choices,
        sep=";",
        quit_str="q",
        opposite=opposite,
        no_selection_value=no_selection_value,
        return_value=return_value,
    )

    assert results == expected
