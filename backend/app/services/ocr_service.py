"""OCR Service for document text extraction."""

import io
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import pytesseract
from pdf2image import convert_from_bytes, convert_from_path
from PIL import Image

logger = logging.getLogger(__name__)


class OCRService:
    """Service for extracting text from images and PDFs using Tesseract OCR."""

    SUPPORTED_IMAGE_FORMATS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"}
    SUPPORTED_PDF_FORMAT = ".pdf"

    def __init__(self, tesseract_cmd: Optional[str] = None, dpi: int = 300):
        """
        Initialize OCR service.

        Args:
            tesseract_cmd: Path to tesseract executable (auto-detected if None)
            dpi: DPI for PDF to image conversion (higher = better quality, slower)
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.dpi = dpi

    def extract_text_from_image(
        self, image: Union[str, Path, bytes, Image.Image], lang: str = "eng"
    ) -> str:
        """
        Extract text from a single image.

        Args:
            image: Image file path, bytes, or PIL Image object
            lang: Language code for OCR (default: English)

        Returns:
            Extracted text string

        Raises:
            ValueError: If image format is not supported
            RuntimeError: If OCR extraction fails
        """
        try:
            if isinstance(image, (str, Path)):
                img = Image.open(image)
            elif isinstance(image, bytes):
                img = Image.open(io.BytesIO(image))
            elif isinstance(image, Image.Image):
                img = image
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")

            # Extract text using Tesseract
            text = pytesseract.image_to_string(img, lang=lang)
            return text.strip()

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise RuntimeError(f"Failed to extract text from image: {e}")

    def extract_text_from_pdf(
        self, pdf: Union[str, Path, bytes], lang: str = "eng", max_pages: Optional[int] = None
    ) -> Dict[int, str]:
        """
        Extract text from PDF by converting pages to images.

        Args:
            pdf: PDF file path or bytes
            lang: Language code for OCR
            max_pages: Maximum number of pages to process (None = all pages)

        Returns:
            Dictionary mapping page number (1-indexed) to extracted text

        Raises:
            RuntimeError: If PDF conversion or OCR fails
        """
        try:
            # Convert PDF to images
            if isinstance(pdf, bytes):
                images = convert_from_bytes(pdf, dpi=self.dpi)
            elif isinstance(pdf, (str, Path)):
                images = convert_from_path(pdf, dpi=self.dpi)
            else:
                raise ValueError(f"Unsupported PDF type: {type(pdf)}")

            # Limit pages if specified
            if max_pages:
                images = images[:max_pages]

            # Extract text from each page
            results = {}
            for page_num, image in enumerate(images, start=1):
                text = self.extract_text_from_image(image, lang=lang)
                results[page_num] = text
                logger.info(f"Extracted {len(text)} characters from page {page_num}")

            return results

        except Exception as e:
            logger.error(f"PDF OCR extraction failed: {e}")
            raise RuntimeError(f"Failed to extract text from PDF: {e}")

    def extract_text_from_file(
        self, file_path: Union[str, Path], lang: str = "eng", max_pages: Optional[int] = None
    ) -> Union[str, Dict[int, str]]:
        """
        Extract text from any supported file type.

        Args:
            file_path: Path to file
            lang: Language code for OCR
            max_pages: Maximum PDF pages to process (ignored for images)

        Returns:
            - For images: Single text string
            - For PDFs: Dictionary mapping page numbers to text

        Raises:
            ValueError: If file format is not supported
            RuntimeError: If extraction fails
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension in self.SUPPORTED_IMAGE_FORMATS:
            return self.extract_text_from_image(path, lang=lang)
        elif extension == self.SUPPORTED_PDF_FORMAT:
            return self.extract_text_from_pdf(path, lang=lang, max_pages=max_pages)
        else:
            raise ValueError(
                f"Unsupported file format: {extension}. "
                f"Supported: {self.SUPPORTED_IMAGE_FORMATS | {self.SUPPORTED_PDF_FORMAT}}"
            )

    def extract_text_from_bytes(
        self,
        file_bytes: bytes,
        file_extension: str,
        lang: str = "eng",
        max_pages: Optional[int] = None,
    ) -> Union[str, Dict[int, str]]:
        """
        Extract text from file bytes.

        Args:
            file_bytes: File content as bytes
            file_extension: File extension (e.g., '.pdf', '.png')
            lang: Language code for OCR
            max_pages: Maximum PDF pages to process

        Returns:
            - For images: Single text string
            - For PDFs: Dictionary mapping page numbers to text
        """
        extension = file_extension.lower()
        if not extension.startswith("."):
            extension = f".{extension}"

        if extension in self.SUPPORTED_IMAGE_FORMATS:
            return self.extract_text_from_image(file_bytes, lang=lang)
        elif extension == self.SUPPORTED_PDF_FORMAT:
            return self.extract_text_from_pdf(file_bytes, lang=lang, max_pages=max_pages)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    def get_text_confidence(self, image: Union[str, Path, bytes, Image.Image]) -> List[Dict]:
        """
        Get OCR confidence scores for each text element.

        Args:
            image: Image to analyze

        Returns:
            List of dictionaries with text and confidence scores
        """
        if isinstance(image, (str, Path)):
            img = Image.open(image)
        elif isinstance(image, bytes):
            img = Image.open(io.BytesIO(image))
        elif isinstance(image, Image.Image):
            img = image
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")

        # Get detailed OCR data
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        results = []
        for i in range(len(data["text"])):
            if data["text"][i].strip():
                results.append(
                    {
                        "text": data["text"][i],
                        "confidence": float(data["conf"][i]),
                        "bbox": {
                            "left": data["left"][i],
                            "top": data["top"][i],
                            "width": data["width"][i],
                            "height": data["height"][i],
                        },
                    }
                )

        return results


# Singleton instance
_ocr_service: Optional[OCRService] = None


def get_ocr_service() -> OCRService:
    """Get or create OCR service singleton."""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service
