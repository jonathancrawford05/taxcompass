"""
Document Ingestor Agent
Extracts structured tax-relevant data from OCR'd documents using LLM
"""
import json
import logging
from typing import Any, Dict, List, Optional

from langchain_community.llms import Ollama

from app.agents.base import BaseAgent
from app.config import settings

logger = logging.getLogger(__name__)


class DocumentIngestorAgent(BaseAgent):
    """
    Agent for extracting structured data from OCR'd documents.

    Uses LLM to parse raw OCR text and extract tax-relevant information
    that can auto-fill the analysis form (UserProfile fields).
    """

    def __init__(self):
        super().__init__(name="document_ingestor")
        self.llm = Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.0,  # Low temperature for deterministic extraction
        )

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from OCR text.

        Args:
            input_data: Dict containing:
                - ocr_text: Raw text extracted from document
                - document_type: Type of document (optional)
                - page_number: Page number if multi-page (optional)

        Returns:
            Dict containing:
                - extracted_fields: Dict mapping UserProfile field names to extracted values
                - confidence: Overall confidence in extraction (0-1)
                - field_confidences: Dict mapping field names to individual confidence scores
                - document_type_detected: Detected document type
                - warnings: List of any issues or warnings
        """
        ocr_text = input_data.get("ocr_text", "")
        document_type = input_data.get("document_type", "unknown")
        page_number = input_data.get("page_number", 1)

        if not ocr_text or not ocr_text.strip():
            return {
                "extracted_fields": {},
                "confidence": 0.0,
                "field_confidences": {},
                "document_type_detected": "unknown",
                "warnings": ["No text provided for extraction"],
            }

        logger.info(
            f"Extracting from {document_type} document (page {page_number}, "
            f"{len(ocr_text)} chars)"
        )

        # Build extraction prompt
        extraction_prompt = self._build_extraction_prompt(ocr_text, document_type)

        try:
            # Call LLM for extraction
            response = self.llm.invoke(extraction_prompt)

            # Parse LLM response
            extracted_data = self._parse_llm_response(response)

            logger.info(
                f"Extracted {len(extracted_data.get('extracted_fields', {}))} fields "
                f"with {extracted_data.get('confidence', 0):.2%} confidence"
            )

            return extracted_data

        except Exception as e:
            logger.error(f"Document extraction failed: {e}")
            return {
                "extracted_fields": {},
                "confidence": 0.0,
                "field_confidences": {},
                "document_type_detected": document_type,
                "warnings": [f"Extraction failed: {str(e)}"],
                "error": str(e),
            }

    def _build_extraction_prompt(self, ocr_text: str, document_type: str) -> str:
        """Build prompt for LLM to extract structured data."""
        return f"""You are a tax document analyzer. Extract structured information from the following OCR text.

DOCUMENT TYPE: {document_type}

OCR TEXT:
{ocr_text[:3000]}

TASK:
Extract tax-relevant information and map it to these fields. Only extract information that is explicitly stated in the document. If a field cannot be determined, mark it as null.

FIELDS TO EXTRACT:
1. Personal Information:
   - citizenship: List of citizenship countries (2-letter ISO codes)
   - current_country: Current residence country (2-letter ISO code)
   - destination_country: Destination/work country (2-letter ISO code)
   - departure_date: Date of departure/move (YYYY-MM-DD format)

2. Family:
   - marital_status: "single", "married", or "common_law"
   - has_spouse: true/false
   - spouse_location: Spouse's country (2-letter ISO code)
   - has_dependents: true/false
   - dependents_location: Dependents' country (2-letter ISO code)

3. Property:
   - owns_home_origin: Owns home in origin country (true/false)
   - home_disposition: "sell", "rent", or "keep_vacant"
   - owns_home_destination: Owns home in destination (true/false)

4. Employment:
   - employment_type: "employee", "self_employed", or "business_owner"
   - employer_country: Country where employer is located (2-letter ISO code)
   - annual_income: Annual income as number (no currency symbols)

5. Financial:
   - has_rental_property: true/false
   - investment_accounts_balance: Total investment balance (number)
   - rrsp_balance: RRSP balance for Canada (number)
   - tfsa_balance: TFSA balance for Canada (number)
   - unrealized_capital_gains: Unrealized gains (number)

6. Document Metadata:
   - document_type_detected: Type of document ("pay_stub", "employment_contract", "bank_statement", "tax_return", "mortgage_statement", "other")
   - confidence: Overall confidence in extraction (0.0 to 1.0)

IMPORTANT EXTRACTION RULES:
- Use ISO 3166-1 alpha-2 country codes (CA=Canada, AE=UAE, US=USA, GB=UK, etc.)
- For dates, use YYYY-MM-DD format
- For monetary amounts, extract only the number (no $, CAD, etc.)
- If information is unclear or not present, use null
- Be conservative - only extract what you're confident about
- Pay stubs may contain: employer name/location, income, tax deductions, YTD earnings
- Employment contracts may contain: job title, salary, start date, location, benefits
- Bank statements may contain: account balances, transaction history, address
- Tax returns may contain: income, deductions, tax paid, RRSP/TFSA contributions

RESPONSE FORMAT:
Return ONLY a valid JSON object with this exact structure:
{{
  "extracted_fields": {{
    "citizenship": ["CA"],
    "current_country": "CA",
    "annual_income": 150000,
    ...only include fields you found...
  }},
  "document_type_detected": "pay_stub",
  "confidence": 0.85,
  "field_confidences": {{
    "annual_income": 0.95,
    "employer_country": 0.80,
    ...confidence for each extracted field...
  }},
  "warnings": ["Could not determine spouse location", "Departure date unclear"]
}}

JSON RESPONSE:"""

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response and extract structured data."""
        try:
            # Try to extract JSON from response
            # LLMs sometimes wrap JSON in markdown code blocks
            response_clean = response.strip()

            # Remove markdown code blocks if present
            if response_clean.startswith("```"):
                # Find content between ``` markers
                lines = response_clean.split("\n")
                json_lines = []
                in_code_block = False
                for line in lines:
                    if line.strip().startswith("```"):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block or (not json_lines and line.strip().startswith("{")):
                        json_lines.append(line)
                response_clean = "\n".join(json_lines)

            # Parse JSON
            data = json.loads(response_clean)

            # Validate structure
            return {
                "extracted_fields": data.get("extracted_fields", {}),
                "confidence": float(data.get("confidence", 0.5)),
                "field_confidences": data.get("field_confidences", {}),
                "document_type_detected": data.get("document_type_detected", "unknown"),
                "warnings": data.get("warnings", []),
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Raw response: {response[:500]}")

            # Fallback: try to extract any useful information manually
            return {
                "extracted_fields": {},
                "confidence": 0.0,
                "field_confidences": {},
                "document_type_detected": "unknown",
                "warnings": [f"Could not parse extraction results: {str(e)}"],
            }

    async def extract_from_multiple_pages(
        self, page_texts: Dict[int, str], document_type: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Extract data from multi-page document.

        Args:
            page_texts: Dict mapping page numbers to OCR text
            document_type: Type of document

        Returns:
            Merged extraction results from all pages
        """
        all_extracted_fields = {}
        all_field_confidences = {}
        all_warnings = []
        page_count = len(page_texts)

        for page_num, page_text in page_texts.items():
            logger.info(f"Processing page {page_num}/{page_count}")

            result = await self.execute(
                {
                    "ocr_text": page_text,
                    "document_type": document_type,
                    "page_number": page_num,
                }
            )

            # Merge extracted fields (later pages can override earlier ones)
            extracted = result.get("extracted_fields", {})
            confidences = result.get("field_confidences", {})

            for field, value in extracted.items():
                # Only override if new value has higher confidence
                new_confidence = confidences.get(field, 0.5)
                existing_confidence = all_field_confidences.get(field, 0.0)

                if new_confidence >= existing_confidence:
                    all_extracted_fields[field] = value
                    all_field_confidences[field] = new_confidence

            all_warnings.extend(result.get("warnings", []))

        # Calculate overall confidence as average of field confidences
        avg_confidence = (
            sum(all_field_confidences.values()) / len(all_field_confidences)
            if all_field_confidences
            else 0.0
        )

        return {
            "extracted_fields": all_extracted_fields,
            "confidence": avg_confidence,
            "field_confidences": all_field_confidences,
            "document_type_detected": document_type,
            "warnings": all_warnings,
            "pages_processed": page_count,
        }


def get_document_ingestor_agent() -> DocumentIngestorAgent:
    """Get or create Document Ingestor Agent singleton."""
    return DocumentIngestorAgent()
