# songbird

Music downloading client featureing mp3 or m4a tagging.

# Installation

You will require:
1. docker: https://docs.docker.com/get-docker/

# Run
If using itunes and google drive (replace the path/to/itunes with the path to your `autoadd to itunes folder`, and replace the `path/to/gdrive` with the path to your google drive folder you store mp3's in)

```bash
docker run -it cboin/songbird:latest --env-file .env -v "path/to/itunesautoadd":"/app/data/itunesauto" -v "path/to/ituneslib":"/app/data/ituneslib" -v "path/to/gdrive":"app/data/gdrive" -v "path/to/local/files":"app/data/dump"

```

# Minimal configuration
By default, the app assumes itunes is installed. At minimum, create a `.env` file with to run without either.

In addition, you need a folder to store local files in. This folder will be passed as a volume mount to the
dockerized app, as above in `-v "path/to/local/files":"app/data/dump"`

Volumeinit will initialize dirs for the docker app to use as bind mounts.
```
task volumeinit
```

```.env
ITUNES_ENABLED=False
GDRIVE_ENABLED=False
```

# To enable gdrive

```.env
GDRIVE_ENABLED=True
GDRIVE_FOLDER_ID=foo
```
Replace the `foo` with the folder id of your google drive folder. This is found
in the url inside the folder when open in googledrive.

`E.x: https://drive.google.com/drive/folders/foo`


Follow https://developers.google.com/drive/api/quickstart/python, and place
the `credentials.json` file at the `app/data/gdrive` folder at the root of the project.

Run

```bash
docker run -it --env-file .env \
-v "${PWD}"/data/dump:/app/data/dump \
-v "${PWD}"/data/local_chromium:/home/appuser/.local/share/pyppeteer/local-chromium \
-v "${PWD}"/credentials.json:/app/credentials.json
```