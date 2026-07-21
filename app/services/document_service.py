import hashlib
from pathlib import Path
from uuid import UUID
import uuid
from fastapi import HTTPException, UploadFile, status
from app.core.constants import ALLOWED_MIME_TYPES, MAX_UPLOAD_SIZE, UPLOAD_DIRECTORY
from app.models.document import Document
from app.models.enums.document_status import DocumentStatus
from app.repositories.document_repository import DocumentRepository

class DocumentService:

    def __init__(self, repository: DocumentRepository):
        self.document_repository = repository
        
    def get_document(self, document_id: UUID) -> Document | None:
        return self.document_repository.get_by_id(document_id)
        
    async def upload_document(self, file: UploadFile):
        self._validate_mime_type(file)

        file_bytes = await self._read_file(file)

        self._validate_file_size(file_bytes)

        checksum = self._calculate_checksum(file_bytes)

        self._check_duplicate(checksum)

        stored_file_name = self._generate_file_name(file.filename)

        storage_path = self._save_file(
            file_bytes,
            stored_file_name,
        )

        document = self._build_document(
            file=file,
            checksum=checksum,
            stored_file_name=stored_file_name,
            storage_path=storage_path,
            file_size=len(file_bytes),
        )

        return self.document_repository.create(document)    
         
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
            print("hi")
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
    
    def _build_document(self, file: UploadFile, checksum: str, stored_file_name: str, storage_path: str, file_size: int) -> Document:
        return Document(
            original_file_name=file.filename,
            stored_file_name=stored_file_name,
            mime_type=file.content_type,
            file_size=file_size,
            checksum=checksum,
            storage_path=storage_path,
            status=DocumentStatus.UPLOADED,
        )