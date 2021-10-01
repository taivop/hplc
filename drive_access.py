import io
import os
from functools import cache
from typing import TextIO

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials

HPLC_CACHE_DIR = os.path.expanduser("~/.hplc_cache")

scopes = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "secrets/biolabautomation-d5dc83b8ddf7.json"
)

drive = build("drive", "v3", credentials=credentials)


def list_files():
    """Get list of files using given drive service."""
    files = []

    page_token = None
    while True:
        response = (
            drive.files()
            .list(
                pageSize=1000,
                fields="nextPageToken, files(id, name, kind, parents)",
                pageToken=page_token,
            )
            .execute()
        )

        response_files = response.get("files", [])
        files += response_files

        page_token = response.get("nextPageToken", None)
        if page_token is None:
            break

    return files


def get_file(file_id: str, use_cache=True) -> TextIO:
    """Download file from Drive"""
    cache_path = os.path.join(HPLC_CACHE_DIR, file_id)
    if use_cache and os.path.isfile(cache_path):
        return open(cache_path, "r")

    request = drive.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    fh.seek(0)

    fulltext = fh.read().decode()

    if use_cache:
        with open(cache_path, "w") as f:
            f.write(fulltext)

    return io.StringIO(fulltext)
