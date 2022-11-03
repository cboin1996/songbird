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

```.env
ITUNES_ENABLED=False
GDRIVE_ENABLED=False
```