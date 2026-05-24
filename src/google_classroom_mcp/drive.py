import io
from functools import lru_cache
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from .auth import get_credentials

GOOGLE_EXPORT_MIME = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "text/plain",
}


@lru_cache(maxsize=1)
def _service():
    return build("drive", "v3", credentials=get_credentials(), cache_discovery=False)


def fetch_file_text(file_id: str, max_bytes: int = 200_000) -> dict[str, Any]:
    """Download a Drive file's content as text. Google-native docs are exported to text/csv.
    Binary files (PDFs, images) return text=None plus a note — Claude can decide what to do."""
    svc = _service()
    meta = svc.files().get(fileId=file_id, fields="id,name,mimeType,size").execute()
    mime = meta["mimeType"]

    if mime in GOOGLE_EXPORT_MIME:
        request = svc.files().export_media(fileId=file_id, mimeType=GOOGLE_EXPORT_MIME[mime])
    else:
        request = svc.files().get_media(fileId=file_id)

    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request, chunksize=max_bytes)
    done = False
    while not done:
        _, done = downloader.next_chunk()
        if buf.tell() >= max_bytes:
            break

    raw = buf.getvalue()[:max_bytes]
    try:
        text = raw.decode("utf-8")
        return {"id": meta["id"], "name": meta["name"], "mime": mime, "text": text, "truncated": buf.tell() > max_bytes}
    except UnicodeDecodeError:
        return {
            "id": meta["id"],
            "name": meta["name"],
            "mime": mime,
            "text": None,
            "bytes_len": len(raw),
            "note": "binary content — not decoded as text",
        }
