# songbird

Music downloading client featureing mp3 or m4a tagging.

# Installation

You will require:
1. docker: https://docs.docker.com/get-docker/

## Run
Note, to be gung-ho, add `--pull always` to any of the below commands to always receive the latest
and greatest immages.

First, initialize your docker volumes

```bash
task volumesinit
```

### Run with itunes and google drive mode enabled
```bash
docker run -it \
-v "${PWD}"/app/data/dump:/app/data/dump \
-v "${PWD}"/app/data/local_chromium:/root/.local/share/pyppeteer/local-chromium \
-v "${PWD}"/app/data/gdrive:/app/data/gdrive \
-v "${PWD}"/path/to/itunesautoadd:/app/data/itunesauto \
-v "${PWD}"/path/to/ituneslib:/app/data/ituneslib \
-p 8080:8080 \
--hostname songbird \
cboin/songbird:latest
```

If using itunes, make sure to replace the following from the above command.
- replace `path/to/itunesautoadd`:
    - MAC - `/Users/*/Music/iTunes/iTunes Media/Automatically Add to Music.localized`
    - WINDOWS - `C:\\Users\*\Music\iTunes\iTunes Media\Automatically Add to Itunes`
- replace `path/to/ituneslib`
    - MAC - `/Users/*/Music/Itunes/Itunes Media/Music`
    - WINDOWS - `C:\\Users\*\Music\iTunes\iTunes Media\Music`

### Minimal configuration
By default, the app assumes itunes is installed. At minimum, create a `.env` file with to run without either.

In addition, you need a folder to store local files in. This folder will be passed as a volume mount to the
dockerized app, as above in `-v "app/data/dump":"app/data/dump", and is initialized automatically when running
`task volumesinit`.

```.env
ITUNES_ENABLED=False
GDRIVE_ENABLED=False
```

### To enable only gdrive
Create a .env file at the root of the project containing:
```.env
ITUNES_ENABLED=false
GDRIVE_FOLDER_ID=foo
```
Replace the `foo` with the folder id of your google drive folder. This is found
in the url inside the folder when open in googledrive.

`E.x: https://drive.google.com/drive/folders/foo`


Follow https://developers.google.com/drive/api/quickstart/python, and place
the `credentials.json` file at the `app/data/gdrive` folder at the root of the project.

```bash
docker run -it --env-file .env \
-v "${PWD}"/app/data/dump:/app/data/dump \
-v "${PWD}"/app/data/local_chromium:/root/.local/share/pyppeteer/local-chromium \
-v "${PWD}"/app/data/gdrive:/app/data/gdrive \
-p 8080:8080 \
--hostname songbird \
cboin/songbird:latest
```

# To enable only itunes
```.env
GDRIVE_ENABLED=false
```

## Run

```bash
docker run -it --env-file .env \
-v "${PWD}"/app/data/dump:/app/data/dump \
-v "${PWD}"/app/data/local_chromium:/root/.local/share/pyppeteer/local-chromium \
-v "${PWD}"/path/to/itunesautoadd:/app/data/itunesauto \
-v "${PWD}"/path/to/ituneslib:/app/data/ituneslib \
cboin/songbird:latest
```
If using itunes, make sure to replace the following from the above command.
- replace `path/to/itunesautoadd`:
    - MAC - `/Users/*/Music/iTunes/iTunes Media/Automatically Add to Music.localized`
    - WINDOWS - `C:\\Users\*\Music\iTunes\iTunes Media\Automatically Add to Itunes`
- replace `path/to/ituneslib`
    - MAC - `/Users/*/Music/Itunes/Itunes Media/Music`
    - WINDOWS - `C:\\Users\*\Music\iTunes\iTunes Media\Music`

# Dev

To run the application locally, you can use a vscode debugger. You should also setup a .env file
with the parameter `RUN_LOCAL=True`.

## Install requirements

```bash
task setup
task install-deps
```

## Run
Vscode debugger can be configured to run the `main.py` file with the following `.vscode/launch.json` file

```json
{
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "./app/main.py",
      "console": "integratedTerminal",
      "justMyCode": true
    },
  ]
}
```

## Linting
To lint the app, run
```
task lint
```

# Configuration
The following table summarizes the configurable parameters for the app, these can be setup in a `.env` file at the root of the project, and passed to docker with `--env-file .env`.
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
| YOUTUBE_RENDER_WAIT        | int           | 2                                 | The wait time before starting a render of the youtube search page          |
| YOUTUBE_HOME_URL           | str           | "https://www.youtube.com"         |                                                                            |
| YOUTUBE_SEARCH_URL         | str           | "https://www.youtube.com/results" |                                                                            |
| YOUTUBE_SEARCH_TAG         | str           | "search_query"                    | The html tag on youtubes home page linking to the html search form         |
| YOUTUBE_SEARCHFORM_PAYLOAD | dict          | {youtube_search_tag: ""}          | the payload for performing a youtube search                                |
| YOUTUBE_DL_RETRIES         | int           | 3                                 | number of retries for youtube-dlp before giving up on a download           |
| FILE_FORMAT                | str           | "mp3"                             | This field is overwritten to m4a if itunes is enabled.                     |
