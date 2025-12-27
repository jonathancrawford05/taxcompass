"""
Document Upload and OCR API Endpoints
Handles document upload, OCR processing, and data extraction
"""
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status, Form
from fastapi.responses import JSONResponse

from app.agents.document_ingestor import get_document_ingestor_agent
from app.services.ocr_service import get_ocr_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload-and-extract", response_model=Dict[str, Any])
async def upload_and_extract(
    file: UploadFile = File(..., description="Document to upload (PDF, PNG, JPG, etc.)"),
    document_type: Optional[str] = Form(
        None, description="Type of document (pay_stub, employment_contract, etc.)"
    ),
    max_pages: Optional[int] = Form(
        None, description="Maximum number of pages to process for PDFs"
    ),
) -> JSONResponse:
    """
    Upload a document, extract text via OCR, and extract structured tax data.

    Supports:
    - Image formats: PNG, JPG, JPEG, TIFF, BMP, GIF
    - PDF documents (all pages or max_pages limit)

    Returns extracted UserProfile fields that can auto-fill the analysis form.

    Example response:
    ```json
    {
      "filename": "paystub.pdf",
      "file_size": 245678,
      "pages_processed": 2,
      "extracted_fields": {
        "employer_country": "AE",
        "annual_income": 150000,
        "employment_type": "employee"
      },
      "confidence": 0.85,
      "field_confidences": {
        "employer_country": 0.90,
        "annual_income": 0.95,
        "employment_type": 0.70
      },
      "document_type_detected": "pay_stub",
      "warnings": []
    }
    ```
    """
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided"
        )

    # Get file extension
    filename_lower = file.filename.lower()
    file_extension = None
    for ext in [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"]:
        if filename_lower.endswith(ext):
            file_extension = ext
            break

    if not file_extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Supported: PDF, PNG, JPG, JPEG, TIFF, BMP, GIF",
        )

    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        logger.info(
            f"Processing uploaded file: {file.filename} "
            f"({file_size} bytes, type: {file_extension})"
        )

        # Validate file size (max 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB",
            )

        # Step 1: OCR text extraction
        ocr_service = get_ocr_service()

        if file_extension == ".pdf":
            # Extract text from PDF (returns dict of page_num -> text)
            ocr_result = ocr_service.extract_text_from_bytes(
                file_bytes=file_content,
                file_extension=file_extension,
                max_pages=max_pages or 10,  # Default to 10 pages max
            )
            pages_processed = len(ocr_result)
            logger.info(f"OCR extracted text from {pages_processed} PDF pages")

        else:
            # Extract text from image (returns single string)
            ocr_result = ocr_service.extract_text_from_bytes(
                file_bytes=file_content, file_extension=file_extension
            )
            pages_processed = 1
            # Convert to dict format for consistency
            ocr_result = {1: ocr_result}
            logger.info(f"OCR extracted {len(ocr_result[1])} characters from image")

        # Step 2: Extract structured data using Document Ingestor Agent
        ingestor = get_document_ingestor_agent()

        if pages_processed > 1:
            # Multi-page extraction (merges results from all pages)
            extraction_result = await ingestor.extract_from_multiple_pages(
                page_texts=ocr_result, document_type=document_type or "unknown"
            )
        else:
            # Single page extraction
            extraction_result = await ingestor.run(
                {
                    "ocr_text": ocr_result[1],
                    "document_type": document_type or "unknown",
                    "page_number": 1,
                }
            )

        # Build response
        response_data = {
            "filename": file.filename,
            "file_size": file_size,
            "file_type": file_extension,
            "pages_processed": pages_processed,
            "extracted_fields": extraction_result.get("extracted_fields", {}),
            "confidence": extraction_result.get("confidence", 0.0),
            "field_confidences": extraction_result.get("field_confidences", {}),
            "document_type_detected": extraction_result.get("document_type_detected", "unknown"),
            "warnings": extraction_result.get("warnings", []),
        }

        logger.info(
            f"Successfully processed {file.filename}: "
            f"extracted {len(response_data['extracted_fields'])} fields "
            f"with {response_data['confidence']:.2%} confidence"
        )

        return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"Document processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}",
        )


@router.post("/extract-from-text", response_model=Dict[str, Any])
async def extract_from_text(
    text: str = Form(..., description="OCR or raw text to extract data from"),
    document_type: Optional[str] = Form(
        None, description="Type of document (pay_stub, employment_contract, etc.)"
    ),
) -> JSONResponse:
    """
    Extract structured tax data from raw text (useful for testing or if OCR is done externally).

    Args:
        text: Raw text content
        document_type: Optional document type hint

    Returns:
        Extracted UserProfile fields
    """
    try:
        if not text or not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No text provided"
            )

        logger.info(
            f"Extracting from raw text ({len(text)} chars, type: {document_type or 'unknown'})"
        )

        # Extract structured data using Document Ingestor Agent
        ingestor = get_document_ingestor_agent()
        extraction_result = await ingestor.run(
            {"ocr_text": text, "document_type": document_type or "unknown", "page_number": 1}
        )

        response_data = {
            "text_length": len(text),
            "extracted_fields": extraction_result.get("extracted_fields", {}),
            "confidence": extraction_result.get("confidence", 0.0),
            "field_confidences": extraction_result.get("field_confidences", {}),
            "document_type_detected": extraction_result.get("document_type_detected", "unknown"),
            "warnings": extraction_result.get("warnings", []),
        }

        logger.info(
            f"Extracted {len(response_data['extracted_fields'])} fields "
            f"with {response_data['confidence']:.2%} confidence"
        )

        return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Text extraction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract data from text: {str(e)}",
        )


@router.get("/supported-formats")
async def get_supported_formats() -> Dict[str, Any]:
    """
    Get list of supported document formats and types.

    Returns information about supported file formats and document types.
    """
    return {
        "supported_file_formats": {
            "images": [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"],
            "documents": [".pdf"],
        },
        "supported_document_types": [
            "pay_stub",
            "employment_contract",
            "bank_statement",
            "tax_return",
            "mortgage_statement",
            "investment_statement",
            "other",
        ],
        "max_file_size_mb": 10,
        "max_pdf_pages_default": 10,
        "extractable_fields": {
            "personal": [
                "citizenship",
                "current_country",
                "destination_country",
                "departure_date",
            ],
            "family": [
                "marital_status",
                "has_spouse",
                "spouse_location",
                "has_dependents",
                "dependents_location",
            ],
            "property": [
                "owns_home_origin",
                "home_disposition",
                "owns_home_destination",
                "has_rental_property",
            ],
            "employment": ["employment_type", "employer_country", "annual_income"],
            "financial": [
                "investment_accounts_balance",
                "rrsp_balance",
                "tfsa_balance",
                "unrealized_capital_gains",
            ],
        },
    }
