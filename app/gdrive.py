import os, sys

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient import http

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def save_song(
    gdrive_folder_id: str,
    credentials_path: str,
    token_path: str,
    song_name: str,
    song_path: str,
    auth_port: int,
    bind_addr: Optional[str] = None,
):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    scopes = ["https://www.googleapis.com/auth/drive"]
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            creds = flow.run_local_server(port=auth_port, bind_addr=bind_addr)
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    logger.debug(f"Loaded credentials: {creds}")
    service = build("drive", "v3", credentials=creds)

    file_metadata = {"name": song_name, "parents": [gdrive_folder_id]}
    media = http.MediaFileUpload(song_path, mimetype="audio/jpeg")
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    file_id = file.get("id")
    logger.info(f"File creation successful -- ID: {file_id}")
    return file_id


if __name__ == "__main__":
    fname = "test.txt"
    fpath = os.path.join(sys.path[0], fname)
    cred_path = os.path.join(sys.path[0], "data", "gdrive", "credentials.json")
    token_path = os.path.join(sys.path[0], "data", "gdrive", "token.json")
    fid = input("Enter folder id: ")
    with open(fpath, "w") as f:
        f.write("swag")
    save_song(fid, cred_path, token_path, "test.txt", fpath, 8080)
    os.remove(fpath)
