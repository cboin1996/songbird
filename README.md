# songbird

Music downloading client featureing mp3 or m4a tagging.

# Installation

You will require:
1. docker: https://docs.docker.com/get-docker/

## Run
If using itunes and google drive (replace the path/to/itunesautoadd with the path to your `autoadd to itunes folder`, and replace the `path/to/ituneslib` with the root of your itunes library

```bash
docker run -it --env-file .env \
-v "${PWD}"app/data/dump:/app/data/dump \
-v "${PWD}"app/data/local_chromium:/root/.local/share/pyppeteer/local-chromium \
-v "${PWD}"app/data/gdrive:/app/data/gdrive \
-v "${PWD}"path/to/itunesautoadd:/app/data/itunesauto \
-v "${PWD}"path/to/ituneslib:/app/data/ituneslib \
cboin/songbird:v0.0.0

```

# Minimal configuration
By default, the app assumes itunes is installed. At minimum, create a `.env` file with to run without either.

In addition, you need a folder to store local files in. This folder will be passed as a volume mount to the
dockerized app, as above in `-v "app/data/dump":"app/data/dump"`

Volumeinit will initialize the minimal dirs for the docker app to use as bind mounts.
```
task volumeinit
```

```.env
ITUNES_ENABLED=False
GDRIVE_ENABLED=False
```

# To enable only gdrive

```.env
GDRIVE_ENABLED=True
GDRIVE_FOLDER_ID=foo
```
Replace the `foo` with the folder id of your google drive folder. This is found
in the url inside the folder when open in googledrive.

`E.x: https://drive.google.com/drive/folders/foo`


Follow https://developers.google.com/drive/api/quickstart/python, and place
the `credentials.json` file at the `app/data/gdrive` folder at the root of the project.

## Run

```bash
docker run -it --env-file .env \
-v "${PWD}"/app/data/dump:/app/data/dump \
-v "${PWD}"/app/data/local_chromium:/root/.local/share/pyppeteer/local-chromium \
-v "${PWD}"/app/data/gdrive:/app/data/gdrive \
cboin/songbird:v0.0.0
```

# To enable only itunes
```.env
ITUNES_ENABLED=True
```

## Run

```bash
docker run -it --env-file .env \
-v "${PWD}"/app/data/dump:/app/data/dump \
-v "${PWD}"/app/data/local_chromium:/root/.local/share/pyppeteer/local-chromium \
-v "${PWD}"/path/to/itunesautoadd:/app/data/itunesauto \
-v "${PWD}"/path/to/ituneslib:/app/data/ituneslib \
cboin/songbird:v0.0.0
```

Replace `path/to/itunesautoadd` with the path to the `automatically add to itunes folder`.
Replace `path/to/ituneslib` with the path to the `itunes library` on your pc.

# Dev
To lint the app, run

```
pip install black
pip install isort
pip install click
```

Then,
```
task lint
```