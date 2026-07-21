import logging
from fastapi import APIRouter, Depends, File, UploadFile
from app.dependencies.document import get_document_service
from app.services.document_service import DocumentService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/document/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service),
):
    return await document_service.upload_document(file)