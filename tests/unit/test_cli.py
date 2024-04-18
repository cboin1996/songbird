from songbirdcli import cli
from songbirdcli import settings
from songbirdcli import version
from io import StringIO
import os, sys, shutil
import pytest

cli_inputs = [
    [
        "jolene",  # user enters jolene
        "0",  # user selects first song
        "",  # user opts to search youtube
        "0",  # user selects first song
        "i",  # save to local itunes folder
        "q",  # user quits
    ],
    [
        "jolene",  # user enters jolene
        "0",  # user selects first song
        "https://www.youtube.com/watch?v=Ixrje2rXLMA",  # user opts to direct download
        "l",  # save locally
        "q",  # user quits
    ],
    [
        "billy joel",  # user enters billy joel
        "-1",  # user selects continue without properties
        "",  # user opts to search youtube
        "0",  # user selects first song
        "l",  # user selects  save locally
        "q",  # user quits
    ],
    [
        "john mayer",  # user enters john mayer
        "",  # user hits enter by accident
        "0",  # user continues by selecting property 0
        "",  # user opts to search youtube
        "",  # user hits enter by accident
        "800",  # user enters invalid input
        "0",  # user selects first song
        "l",  # user selects  save locally
        "q",  # user quits
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
