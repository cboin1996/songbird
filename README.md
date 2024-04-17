# songbirdcli 🐦

Music downloading client featuring mp3 or m4a tagging.

## Install via Docker

To run the app via docker, you will require:
1. docker: https://docs.docker.com/get-docker/

Note: to be gung-ho, add `--pull always` to any of the
below commands to always receive the latest
and greatest images.

First, initialize your docker volumes

```bash
make volumesinit
```

Note: bash or zsh aliases are provided below,
assuming you clone songbird into your home directory
into `~/proj/cboin1996/`.

### Itunes and Google Drive Integration

Macos:

```bash
alias songbirdgi="docker run -it --env-file "${HOME}"/proj/cboin1996/songbird/songbirdcli/songbirdcli/docker.env \
	-v "${HOME}"/proj/cboin1996/songbird/songbirdcli/songbirdcli/data/dump:/app/data/dump \
	-v "${HOME}"/proj/cboin1996/songbird/songbirdcli/songbirdcli/data/gdrive:/app/data/gdrive \
    -v "${HOME}"/Music/iTunes/iTunes\ Media/Automatically\ Add\ to\ Music.localized:/app/data/itunesauto \
    -v "${HOME}"/Music/Itunes/Itunes\ Media/Music:/app/data/ituneslib \
	-p 8080:8080 \
	--hostname songbird \
	--pull always \
	cboin/songbird:latest"
```

Windows:

Install windows sub-system for linux and setup the below alias:

```bash
alias songbirdgi="docker run -it --env-file "${HOME}"/proj/cboin1996/songbird/songbirdcli/songbirdcli/docker.env \
	-v "${HOME}"/proj/cboin1996/songbird/songbirdcli/songbirdcli/data/dump:/app/data/dump \
	-v "${HOME}"/proj/cboin1996/songbird/songbirdcli/songbirdcli/data/gdrive:/app/data/gdrive \
    -v /mnt/c/Users/*/Music/iTunes/iTunes\ Media/Automatically\ Add\ to\ Music:/app/data/itunesauto \
    -v /mnt/c/Users/*/Music/iTunes/iTunes\ Media/Music:/app/data/ituneslib \
	-p 8080:8080 \
	--hostname songbird \
	--pull always \
	cboin/songbird:latest"
```

### Minimal configuration

By default, the app assumes itunes is installed. At minimum,
create a `.env` file with to run without either.

In addition, you need a folder to store local files in.
This folder will be passed as a volume mount to the
dockerized app, as above in `-v "app/data/dump":"app/data/dump",
and is initialized automatically when running
`make volumesinit`.

```.env
ITUNES_ENABLED=False
GDRIVE_ENABLED=False
```

### Gdrive Only

Create a .env file at the root of the project containing:
```.env
ITUNES_ENABLED=false
GDRIVE_FOLDER_ID=foo
```
Replace the `foo` with the folder id of your google drive
folder. This is found
in the url inside the folder when open in googledrive.

`E.x: https://drive.google.com/drive/folders/foo`


Follow https://developers.google.com/drive/api/quickstart/python,
and place the `credentials.json` file at the `app/data/gdrive`
folder at the root of the project.

```bash
alias songbirdg="docker run -it --env-file "${HOME}"/proj/cboin1996/songbird/songbirdcli/songbirdcli/docker.env \
	-v "${HOME}"/proj/cboin1996/songbird/songbirdcli/songbirdcli/data/dump:/app/data/dump \
	-v "${HOME}"/proj/cboin1996/songbird/songbirdcli/songbirdcli/data/gdrive:/app/data/gdrive \
	-p 8080:8080 \
	--hostname songbird \
	--pull always \
	cboin/songbird:latest"
```

### Itunes Only

```.env
GDRIVE_ENABLED=false
```

## Run

Macos:

```bash
alias songbirdi="docker run -it --env-file "${HOME}"/proj/cboin1996/songbird/songbirdcli/songbirdcli/docker.env \
        -v "${HOME}"/proj/cboin1996/songbird/songbirdcli/songbirdcli/data/dump:/app/data/dump \
        -v "${HOME}"/Music/iTunes/iTunes\ Media/Automatically\ Add\ to\ Music.localized:/app/data/itunesauto \
        -v "${HOME}"/Music/Itunes/Itunes\ Media/Music:/app/data/ituneslib \
	--pull always \
        cboin/songbird:latest"
```

Windows:

Install windows sub-system for linux and
setup the below alias:

```bash
alias songbirdi="docker run -it --env-file "${HOME}"/proj/cboin1996/songbird/songbirdcli/songbirdcli/docker.env \
	-v "${HOME}"/proj/cboin1996/songbird/songbirdcli/songbirdcli/data/dump:/app/data/dump \
    -v /mnt/c/Users/*/Music/iTunes/iTunes\ Media/Automatically\ Add\ to\ Music:/app/data/itunesauto \
    -v /mnt/c/Users/*/Music/iTunes/iTunes\ Media/Music:/app/data/ituneslib \
	-p 8080:8080 \
	--hostname songbird \
	--pull always \
	cboin/songbird:latest"
```

## Install as Package

To use songbirdcli as a python package, use
```bash
pip install songbirdcli
```

See [tests](./tests/unit/test_cli.py) for an example
of configuring and running songbirdcli as a package.

For API documentation, view [here](https://cboin1996.github.io/songbird/)

## Development

To run the application locally, you can use a vscode debugger.
You should also setup a .env file
with the parameter `RUN_LOCAL=True`.

### Requirements

1. Clone [songbirdcore](https://github.com/cboin1996/songbirdcore.git)
adjacent to this project.

2. Next, run

	```bash
	export ENV=dev
	make setup
	```

3. Follow the outputted instructions from `make setup`.

4. Next, run:

	```bash
	make requirements
	```

**Note: the above command performs an editable install of `songbirdcore`**

This allows you to edit `songbirdcore` locally,
and have those changes directly
integrated with this application when developing.
To install the official stable version use

```bash
pip install songbirdcore
```

### Debug CLI

Vscode debugger can be configured to run the `cli.py` file
with the following `.vscode/launch.json` file

```json
{
	"configurations": [
		{
			"name": "Python: Current File",
			"type": "python",
			"request": "launch",
			"program": "./songbirdcli/cli.py",
			"console": "integratedTerminal",
			"justMyCode": true,
			"envFile": "./dev.env"
		},
	]
}
```

Alternatively, you can simply run the app directly with

```bash
python3 songbirdcli/cli.py
```

## Linting

To lint the app, run

```
make lint
```

## Configuration

The following table summarizes the configurable parameters for the app,
these can be setup in a `.env` file at the root of the project,
and passed to docker with `--env-file .env`.

| Variable                   | Type          | Default                           | Description                                                                |
| -------------------------- | ------------- | --------------------------------- | -------------------------------------------------------------------------- |
| RUN_LOCAL                  | bool          | False                             | Whether to run the app locally, or configure it for running in a container |
| ROOT_PATH                  | str           | sys.path[0]                       | The root path to the project folder                                        |
| DATA_PATH                  | str           | "data"                            | The name of the folder where app data is stored on disk                    |
| ITUNES_SEARCH_API_BASE_URL | str           | "https://itunes.apple.com/search" | The itunes search api root url                                             |
| ITUNES_ENABLED             | bool          | True                              | Whether to run with itunes integration enabled                             |
| ITUNES_FOLDER_PATH         | Optional[str] | "itunesauto"                      | The path to the itunes automatically add folder                            |
| ITUNES_LIB_PATH            | Optional[str] | "ituneslib"                       | The path to the itunes library folder                                      |
| GDRIVE_ENABLED             | bool          | True                              | Whether to run with google drive integration                               |
| GDRIVE_FOLDER_PATH         | Optional[str] | "gdrive"                          | Local folder for storing files destined for uploading to google drive      |
| GDRIVE_FOLDER_ID           | Optional[str] | ""                                | The folder id of a cloud google drive folder                               |
| GDRIVE_AUTH_PORT           | int           | 8080                              | The port for oauth setup for google drive integration                      |
| LOCAL_SONG_STORE_STR       | str           | "dump"                            | Where songs are stored locally                                             |
| FNAME_DUP_KEY              | str           | "_dup"                            | The key for naming duplicate files                                         |
| FNAME_DUP_LIMIT            | str           | 8                                 | The limit of duplicate files matching the `FNAME_DUP_KEY`                  |
| YOUTUBE_DL_ENABLED         | bool          | True                              | Whether to enable the youtube download feature                             |
| YOUTUBE_RENDER_TIMEOUT     | int           | 20                                | The time before giving up on the render of youtube's search page           |
| YOUTUBE_RENDER_WAIT        | float         | 0.2                               | The wait time before starting a render of the youtube search page          |
| YOUTUBE_RENDER_SLEEP       | int           | 1                                 | The wait time after initial render of youtube                              |
| YOUTUBE_HOME_URL           | str           | "https://www.youtube.com"         |                                                                            |
| YOUTUBE_SEARCH_URL         | str           | "https://www.youtube.com/results" |                                                                            |
| YOUTUBE_SEARCH_TAG         | str           | "search_query"                    | The html tag on youtubes home page linking to the html search form         |
| YOUTUBE_SEARCHFORM_PAYLOAD | dict          | {youtube_search_tag: ""}          | the payload for performing a youtube search                                |
| YOUTUBE_DL_RETRIES         | int           | 3                                 | number of retries for youtube-dlp before giving up on a download           |
| FILE_FORMAT                | str           | "mp3"                             | This field is overwritten to m4a if itunes is enabled.                     |
