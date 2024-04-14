from songbirdcli import cli
from songbirdcli import settings
from songbirdcli import version


def test_cli(monkeypatch):
    # TODO: implement end to end test example
    inputs = iter(["jolene", "y", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    config = settings.SongbirdCliConfig(version=version.version)
    try:
        cli.run(config=config)
    except Exception as e:
        assert False, f"'run()' threw an uncaught exception."
