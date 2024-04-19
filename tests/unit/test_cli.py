from songbirdcli import cli
from songbirdcli import settings
from songbirdcli import version
from io import StringIO
import os, sys, shutil
import pytest

# cli_inputs defined vectors that a user would
# input as they navigate through the app
cli_inputs = [
    [
        "jolene",  # user enters jolene
        "0",  # user selects first song
        "",  # user opts to search youtube
        "0",  # user selects first song
        "i",  # save to local itunes folder
        "q",  # user quits
        "y",  # user quits via y/n selection
    ],
    [
        "jolene",  # user enters jolene
        "0",  # user selects first song
        "https://s"  # user enter invalid download url
        "https://www.youtube.com/watch?v=Ixrje2rXLMA",  # user opts to direct download
        "l",  # save locally
        "q",  # user quits
        "n",  # user selects to continue
        "billy",  # user searches billy
        "0",  # user selects first song
        "q",  # user quits to main menu
        "q",  # user quits app
        "q",  # user confirms quit
    ],
    [
        "billy joel; john lennon",  # user enters billy joel and john lennon
        "-1",  # user selects continue without properties
        "",  # user opts to search youtube
        "",  # user hits enter by accident
        "800",  # user enters invalid input
        "0",  # user selects first song
        "l",  # user selects  save locally
        "q",  # user accidentally quits
        "y",  # user selects to resume
        "0",  # user selects property 0
        "q",  # user quits to main menu
        "q",  # user quits app
        "y",  # user quits app
    ],
    [
        "album",  # user enters album mode
        "billy joel the stranger",  # user enters billy joel
        "",  # validation for empty input
        "-5",  # user enters invalid value
        "0",  # user selects album 0
        "-1",  # user selects keep all songs
        "-5",  # user enters invalid input
        "0",  # user selects song property 0 for first song
        "",  # user hits enter to search youtube
        "0",  # user selects song 0
        "l",  # save locally
        "q",  # select quit
        "y",  # continue with queued songs
        "0",  # select property 0
        "q",  # quit queued songs
        "n",  # do not continue queue
        "q",  # quit application
        "y",  # set yes to are you sure message
    ],
]


@pytest.fixture
def create_test_folder():
    tests_data_folder = os.path.join(sys.path[0], "tests-output")
    if not os.path.exists(tests_data_folder):
        os.mkdir(tests_data_folder)
    yield tests_data_folder
    # test cleanup
    shutil.rmtree(tests_data_folder)


@pytest.fixture
def load_m4a_config(create_test_folder, monkeypatch, request):
    # below are parametrized vectorized inputs that
    # a user would enter if downloading a song
    inputs = iter(request.param)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    # create tests-output folder
    tests_data_folder = create_test_folder
    config = settings.SongbirdCliConfig(
        version=version.version,
        root_path=tests_data_folder,
        gdrive_enabled=False,
        itunes_enabled=True,
        file_format="m4a",
        # we set these paths explicitly so that test
        # directories are used
        # in real world scenario, these values
        # could be set to the actual itunes folders
        # as long as run_local is true.
        itunes_lib_path=os.path.join(tests_data_folder, "mock-itunes-lib"),
        itunes_folder_path=os.path.join(tests_data_folder, "mock-itunes-auto-folder"),
        run_local=True,
    )
    return config


@pytest.fixture
def load_mp3_config(create_test_folder, monkeypatch, request):
    # below are parametrized vectorized inputs that
    # a user would enter if downloading a song
    inputs = iter(request.param)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    # create tests-output folder
    tests_data_folder = create_test_folder
    config = settings.SongbirdCliConfig(
        version=version.version,
        root_path=tests_data_folder,
        gdrive_enabled=False,
        itunes_enabled=True,
        file_format="mp3",
        # we set these paths explicitly so that test
        # directories are used
        # in real world scenario, these values
        # could be set to the actual itunes folders
        # as long as run_local is true.
        itunes_lib_path=os.path.join(tests_data_folder, "mock-itunes-lib"),
        itunes_folder_path=os.path.join(tests_data_folder, "mock-itunes-auto-folder"),
        run_local=True,
    )
    return config


@pytest.mark.parametrize("load_mp3_config", cli_inputs, indirect=True)
def test_cli_mp3(load_mp3_config):
    # invoke the main function of the cli
    cli.run(config=load_mp3_config)


@pytest.mark.parametrize("load_m4a_config", cli_inputs, indirect=True)
def test_cli_m4a(load_m4a_config):
    # invoke the main function of the cli
    cli.run(config=load_m4a_config)
