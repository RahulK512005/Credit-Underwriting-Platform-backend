from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from pathlib import Path
from app.database import get_db
from app.models import Entity, Document, EntityStatus
from app.config import settings
from app.services import extraction_service

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_EXTENSIONS = {'.pdf', '.xlsx', '.xls'}


@router.post("")
async def upload_document(
    entity_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload document for an entity with auto-classification
    """
    # Validate entity exists
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found"
        )
    
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    # Save file
    try:
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Extract and classify document
    try:
        if file_ext == '.pdf':
            extracted_data, doc_type, confidence = extraction_service.extract_from_pdf(content)
        elif file_ext in {'.xlsx', '.xls'}:
            extracted_data, doc_type, confidence = extraction_service.extract_from_excel(content)
        else:
            extracted_data, doc_type, confidence = {}, "unknown", 0.0
    except Exception as e:
        extracted_data = {"error": str(e)}
        doc_type = "unknown"
        confidence = 0.0
    
    # Create document record
    document = Document(
        entity_id=entity_id,
        filename=file.filename,
        file_path=file_path,
        file_type=file_ext[1:],
        document_class=doc_type,
        classification_confidence=confidence
    )
    
    db.add(document)
    
    # Update entity status
    if entity.status == EntityStatus.ONBOARDED:
        entity.status = EntityStatus.DOCUMENTS_UPLOADED
    
    db.commit()
    db.refresh(document)
    
    return {
        "document_id": document.id,
        "filename": document.filename,
        "document_type": doc_type,
        "confidence": confidence,
        "extracted_data": extracted_data,
        "message": "Document uploaded and classified successfully"
    }


@router.get("/entity/{entity_id}")
def get_entity_documents(
    entity_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all documents for an entity
    """
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found"
        )
    
    documents = db.query(Document).filter(Document.entity_id == entity_id).all()
    
    return {
        "entity_id": entity_id,
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "document_class": doc.document_class,
                "classification_confidence": doc.classification_confidence,
                "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None
            }
            for doc in documents
        ]
    }


@router.put("/{document_id}/reclassify")
def reclassify_document(
    document_id: int,
    document_class: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Override document classification
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Validate document class
    valid_classes = ["annual_report", "borrowing_profile", "unknown"]
    if document_class not in valid_classes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document class. Must be one of: {', '.join(valid_classes)}"
        )
    
    document.document_class = document_class
    document.classification_confidence = 1.0  # Manual override = 100% confidence
    
    db.commit()
    db.refresh(document)
    
    return {
        "document_id": document.id,
        "document_class": document.document_class,
        "message": "Document classification updated"
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a document
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Delete file from storage
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception:
        pass  # Continue even if file deletion fails
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}
