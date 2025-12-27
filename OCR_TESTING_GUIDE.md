# OCR Document Ingestion Testing Guide

This guide explains how to test the newly implemented OCR document ingestion and auto-fill functionality in TaxCompass.

## What Was Implemented

### Backend Components

1. **OCR Service** (`backend/app/services/ocr_service.py`)
   - Extracts text from images (PNG, JPG, TIFF, BMP, GIF)
   - Extracts text from PDFs (converts pages to images, then OCR)
   - Supports multi-page PDF processing
   - Returns confidence scores for OCR quality

2. **Document Ingestor Agent** (`backend/app/agents/document_ingestor.py`)
   - Uses Ollama LLM to parse OCR text
   - Extracts structured tax-relevant data
   - Maps extracted data to UserProfile fields
   - Provides field-level confidence scores
   - Handles multi-page document merging

3. **Document Upload API** (`backend/app/api/v1/documents.py`)
   - `POST /api/v1/documents/upload-and-extract` - Upload and process documents
   - `POST /api/v1/documents/extract-from-text` - Process raw text
   - `GET /api/v1/documents/supported-formats` - Get supported formats info

### Frontend Components

1. **FileUpload Component** (`frontend/src/components/FileUpload.tsx`)
   - File selection with drag-and-drop
   - Upload progress indication
   - Extraction results display
   - Confidence score visualization
   - Warnings and errors display

2. **Analysis Page Integration** (`frontend/src/app/analysis/page.tsx`)
   - Auto-fill form fields from extracted data
   - Preserve user edits while allowing extraction
   - Clear visual feedback

## Prerequisites

Before testing, you need to rebuild the Docker containers to include the new dependencies:

```bash
# Stop existing containers
docker compose down

# Rebuild with new dependencies
docker compose build

# Start containers
docker compose up -d

# Check that all services are running
docker compose ps
```

### Verify Backend Dependencies

Check that tesseract and poppler are installed in the backend container:

```bash
docker compose exec backend tesseract --version
docker compose exec backend pdftotext -v
```

You should see version output for both commands.

## Testing Scenarios

### 1. Test with Sample Pay Stub

Create a simple pay stub as a test document. Here's a sample you can create as a text file and convert to PDF:

```
XYZ COMPANY LIMITED
Dubai, United Arab Emirates

PAY STUB - January 2025

Employee: John Doe
Employee ID: 12345
Position: Software Engineer

Gross Salary: AED 25,000.00
Monthly Total: AED 25,000.00

Year to Date Earnings: AED 25,000.00

Employment Start Date: June 1, 2025
```

**Expected Extraction:**
- `employer_country`: "AE"
- `annual_income`: 300000 (25000 * 12)
- `employment_type`: "employee"
- `destination_country`: "AE"
- `departure_date`: "2025-06-01"

### 2. Test with Employment Contract

Create a simple employment contract:

```
EMPLOYMENT CONTRACT

This agreement is made between:
XYZ Company Ltd., registered in United Arab Emirates
and
John Doe, Canadian citizen currently residing in Canada

Position: Senior Software Engineer
Start Date: June 1, 2025
Location: Dubai, UAE
Annual Salary: USD 150,000

The employee will relocate from Canada to the United Arab Emirates.

Family Status: Married
Spouse will remain in Canada initially.
```

**Expected Extraction:**
- `citizenship`: ["CA"]
- `current_country`: "CA"
- `destination_country`: "AE"
- `departure_date`: "2025-06-01"
- `employment_type`: "employee"
- `employer_country`: "AE"
- `annual_income`: 150000
- `marital_status`: "married"
- `has_spouse`: true
- `spouse_location`: "CA"

### 3. Test via Frontend UI

1. **Navigate to Analysis Page:**
   ```
   http://localhost:3000/analysis
   ```

2. **Upload Document:**
   - Click "Select Document" button
   - Choose your test PDF or image
   - Click "Upload & Extract Data"

3. **Review Extraction Results:**
   - Check the confidence score (should be > 60%)
   - Review extracted fields
   - Check for any warnings

4. **Verify Auto-Fill:**
   - Scroll down to the form fields
   - Verify that extracted data has populated the form
   - Manually adjust any incorrect values

5. **Run Analysis:**
   - Click "Run Analysis" button
   - Verify that the analysis completes successfully
   - Review the results

### 4. Test via API (Postman/curl)

**Upload and Extract:**

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload-and-extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/paystub.pdf" \
  -F "document_type=pay_stub"
```

**Expected Response:**

```json
{
  "filename": "paystub.pdf",
  "file_size": 12345,
  "file_type": ".pdf",
  "pages_processed": 1,
  "extracted_fields": {
    "employer_country": "AE",
    "annual_income": 300000,
    "employment_type": "employee",
    "destination_country": "AE"
  },
  "confidence": 0.85,
  "field_confidences": {
    "employer_country": 0.90,
    "annual_income": 0.95,
    "employment_type": 0.80,
    "destination_country": 0.90
  },
  "document_type_detected": "pay_stub",
  "warnings": []
}
```

**Extract from Text:**

```bash
curl -X POST "http://localhost:8000/api/v1/documents/extract-from-text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Employee: John Doe, Salary: AED 25000, Company: Dubai Tech Ltd" \
  -d "document_type=pay_stub"
```

**Get Supported Formats:**

```bash
curl http://localhost:8000/api/v1/documents/supported-formats
```

## Validation Checklist

- [ ] Backend container has tesseract-ocr installed
- [ ] Backend container has poppler-utils installed
- [ ] OCR extracts text from uploaded PDF
- [ ] OCR extracts text from uploaded image
- [ ] Document Ingestor Agent parses OCR text
- [ ] Extracted fields map to UserProfile schema
- [ ] Confidence scores are reasonable (> 0.5)
- [ ] Frontend displays extraction results
- [ ] Form fields auto-fill with extracted data
- [ ] User can override auto-filled values
- [ ] Full analysis workflow completes successfully
- [ ] API endpoints return proper error messages for invalid inputs

## Common Issues and Solutions

### Issue: "tesseract: command not found"

**Solution:** Rebuild the backend Docker container:
```bash
docker compose build backend
docker compose up -d backend
```

### Issue: Low confidence scores (< 0.5)

**Causes:**
- Poor image quality
- Handwritten text
- Complex layouts
- Non-standard formatting

**Solutions:**
- Use higher resolution scans (300+ DPI)
- Ensure good contrast
- Use standard document templates
- Test with digital PDFs rather than scanned images

### Issue: Incorrect field extraction

**Causes:**
- LLM misinterpreting context
- Ambiguous document format
- Missing information in document

**Solutions:**
- Provide `document_type` hint when uploading
- Use standardized document formats
- Include clear labels in documents
- Manually review and correct extracted data

### Issue: "File too large" error

**Solution:**
- Maximum file size is 10MB
- Compress PDF or reduce image quality
- For multi-page PDFs, use `max_pages` parameter

## Performance Notes

- **Image OCR:** ~2-5 seconds per page
- **PDF OCR:** ~3-8 seconds per page
- **LLM Extraction:** ~5-15 seconds depending on text length
- **Total for 1-page document:** ~10-25 seconds

The processing time depends on:
- Document size and complexity
- Ollama LLM performance
- System resources

## Next Steps

After successful testing, consider:

1. **Add more document types:**
   - Bank statements
   - Tax returns
   - Mortgage statements
   - Investment statements

2. **Improve extraction accuracy:**
   - Fine-tune LLM prompts
   - Add document-specific extraction rules
   - Implement fallback extraction methods

3. **Enhance UI/UX:**
   - Add drag-and-drop file upload
   - Show extraction progress
   - Allow editing extracted fields before auto-fill
   - Save uploaded documents for audit trail

4. **Add advanced features:**
   - Batch document processing
   - Document validation and verification
   - Automatic document type detection
   - Multi-language OCR support

## Troubleshooting

Enable debug logging to see detailed extraction information:

```bash
# View backend logs
docker compose logs -f backend

# Filter for OCR-related logs
docker compose logs backend | grep -i "ocr\|extraction\|document"
```

Check the LLM response to understand extraction logic:

```python
# In backend/app/agents/document_ingestor.py
# Temporarily add this after LLM call:
logger.info(f"LLM Raw Response: {response}")
```

## Support

If you encounter issues:

1. Check the logs for error messages
2. Verify all dependencies are installed
3. Test with simple, clear documents first
4. Ensure Ollama is running and accessible
5. Review the API documentation at http://localhost:8000/api/docs
