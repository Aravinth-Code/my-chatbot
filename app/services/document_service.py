import hashlib
import uuid
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status

from app.core.constants import ALLOWED_MIME_TYPES, MAX_UPLOAD_SIZE, UPLOAD_DIRECTORY, WEB_CONTENT_TYPE
from app.models.document import Document
from app.models.enums.document_source_type import DocumentSourceType
from app.models.enums.document_status import DocumentStatus
from app.pipeline.cleaners.text_cleaner import TextCleaner
from app.pipeline.extractors.extractor import Extractor
from app.pipeline.loaders.url_fetcher import UrlFetcher
from app.repositories.document_contents_repository import DocumentContentsRepository
from app.repositories.document_repository import DocumentRepository
from app.services.document_chunk_service import DocumentChunkService
from app.services.embedding_service import EmbeddingService

class DocumentService:

    def __init__(self,
                 document_repository: DocumentRepository,
                 document_contents_repository: DocumentContentsRepository,
                 pdf_extractor: Extractor,
                 web_extractor: Extractor,
                 url_fetcher: UrlFetcher,
                 text_cleaner: TextCleaner,
                 document_chunk_service: DocumentChunkService,
                 embedding_service: EmbeddingService):

        self.document_repository = document_repository
        self.document_contents_repository = document_contents_repository
        self.pdf_extractor = pdf_extractor
        self.web_extractor = web_extractor
        self.url_fetcher = url_fetcher
        self.text_cleaner = text_cleaner
        self.document_chunk_service = document_chunk_service
        self.embedding_service = embedding_service

    def get_document(self, document_id: UUID) -> Document | None:
        return self.document_repository.get_by_id(document_id)

    async def upload_document(self, file: UploadFile) -> Document:
        self._validate_mime_type(file)

        file_bytes = await self._read_file(file)

        self._validate_file_size(file_bytes)

        checksum = self._calculate_checksum(file_bytes)

        self._check_duplicate(checksum)

        stored_file_name = self._generate_file_name(file.filename)

        storage_path = self._save_file(file_bytes, stored_file_name)

        document = self.document_repository.create(
            Document(
                original_file_name=file.filename,
                stored_file_name=stored_file_name,
                mime_type=file.content_type,
                file_size=len(file_bytes),
                checksum=checksum,
                storage_path=storage_path,
                status=DocumentStatus.UPLOADED,
                source_type=DocumentSourceType.FILE,
            )
        )

        return self._process_document(document, file_bytes, self.pdf_extractor)

    def ingest_url(self, url: str) -> Document:
        content = self.url_fetcher.fetch(url)

        checksum = self._calculate_checksum(content)

        self._check_duplicate(checksum)

        stored_file_name = f"{uuid.uuid4()}.html"

        storage_path = self._save_file(content, stored_file_name)

        document = self.document_repository.create(
            Document(
                original_file_name=url,
                stored_file_name=stored_file_name,
                mime_type=WEB_CONTENT_TYPE,
                file_size=len(content),
                checksum=checksum,
                storage_path=storage_path,
                status=DocumentStatus.UPLOADED,
                source_type=DocumentSourceType.URL,
                source_url=url,
            )
        )

        return self._process_document(document, content, self.web_extractor)

    def _process_document(self, document: Document, content: bytes, extractor: Extractor) -> Document:
        self.document_repository.update_status(document, DocumentStatus.PROCESSING)

        try:
            self.document_repository.update_status(document, DocumentStatus.EXTRACTING)

            contents = extractor.extract(document_id=document.id, content=content)
            contents = self.text_cleaner.clean_document_content(docs=contents)

            self.document_repository.update_status(document, DocumentStatus.EXTRACTED)

        except Exception:
            self.document_repository.update_status(document, DocumentStatus.FAILED)
            raise

        self.document_contents_repository.create_many(contents)

        try:
            self.document_repository.update_status(document, DocumentStatus.CHUNKING)

            self.document_chunk_service.chunk_document(document.id)

        except Exception:
            self.document_repository.update_status(document, DocumentStatus.FAILED)
            raise

        try:
            self.document_repository.update_status(document, DocumentStatus.EMBEDDING)

            self.embedding_service.embed_document(document.id)

        except Exception:
            self.document_repository.update_status(document, DocumentStatus.FAILED)
            raise

        self.document_repository.update_status(document, DocumentStatus.PROCESSED)

        return document

    def _validate_mime_type(self, file: UploadFile):
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported."
            )

    async def _read_file(self, file: UploadFile) -> bytes:
        file_bytes = await file.read()
        await file.seek(0)
        return file_bytes

    def _validate_file_size(self, file_bytes: bytes):
        if len(file_bytes) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds maximum limit."
            )

    def _calculate_checksum(self, file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    def _check_duplicate(self, checksum: str):
        document = self.document_repository.get_by_checksum(checksum)
        if document:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document already exists."
            )

    def _generate_file_name(self, original_file_name: str) -> str:
        extension = Path(original_file_name).suffix
        return f"{uuid.uuid4()}{extension}"

    def _save_file(self, file_bytes: bytes, stored_file_name: str) -> str:
        UPLOAD_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = UPLOAD_DIRECTORY / stored_file_name
        with open(file_path, "wb") as file:
            file.write(file_bytes)

        return str(file_path)
