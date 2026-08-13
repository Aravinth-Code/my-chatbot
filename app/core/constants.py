from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

PDF_MIME_TYPE = "application/pdf"
MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20 MB

ALLOWED_MIME_TYPES = {
    "application/pdf",
}

UPLOAD_DIRECTORY = Path("storage/uploads")

WEB_CONTENT_TYPE = "text/html"
MAX_URL_CONTENT_SIZE = 5 * 1024 * 1024  # 5 MB
URL_FETCH_TIMEOUT_SECONDS = 10
