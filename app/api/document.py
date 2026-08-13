import logging
from fastapi import APIRouter, Depends, File, UploadFile
from app.dependencies.document import get_document_service
from app.schemas.document import IngestUrlRequest
from app.services.document_service import DocumentService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/document/upload")
async def upload_document(file: UploadFile = File(...), document_service: DocumentService = Depends(get_document_service)):
    return await document_service.upload_document(file)

@router.post("/document/ingesturl")
def ingest_url(request: IngestUrlRequest, document_service: DocumentService = Depends(get_document_service)):
    return document_service.ingest_url(str(request.url))