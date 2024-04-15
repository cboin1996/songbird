from songbirdcli import cli
from songbirdcli import settings
from songbirdcli import version
from io import StringIO
import os, sys, shutil
import pytest


@pytest.fixture()
def load_config(monkeypatch, request):
    # below are parametrized vectorized inputs that
    # a user would enter if downloading a song
    inputs = iter(request.param)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    # create tests-output folder
    tests_data_folder = os.path.join(sys.path[0], "tests-output")
    if not os.path.exists(tests_data_folder):
        os.mkdir(tests_data_folder)
    config = settings.SongbirdCliConfig(
        version=version.version,
        root_path=tests_data_folder,
        gdrive_enabled=False,
        itunes_enabled=True,
        # we set these paths explicitly so that test
        # directories are used
        # in real world scenario, these values
        # could be set to the actual itunes folders
        # as long as run_local is true.
        itunes_lib_path=os.path.join(tests_data_folder, "mock-itunes-lib"),
        itunes_folder_path=os.path.join(tests_data_folder, "mock-itunes-auto-folder"),
        run_local=True,
    )
    # yield setup to test
    yield config

    # test cleanup
    shutil.rmtree(tests_data_folder)


@pytest.mark.parametrize(
    "load_config",
    [
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
    ],
    indirect=True,
)
def test_cli_default(load_config):
    # invoke the make function of the cli
    cli.run(config=load_config)
