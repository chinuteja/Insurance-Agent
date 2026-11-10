
from pathlib import Path

from pypdf import PdfReader
from docx import Document


class DocumentExtractionService:

    SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx"}

    def extract_text(self, file_path: str) -> dict:

        path = Path(file_path)

        # Validate file existence
        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        # Validate file extension
        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported document format: {extension}"
            )

        # Extract based on file format
        if extension == ".pdf":
            return self._extract_pdf(path)

        if extension == ".txt":
            return self._extract_txt(path)

        if extension == ".docx":
            return self._extract_docx(path)

        raise ValueError("Unable to process document.")

    def _extract_pdf(self, path: Path) -> dict:

        reader = PdfReader(str(path))

        if reader.is_encrypted:
            raise ValueError(
                "Encrypted PDF documents are not supported."
            )

        extracted_pages = []

        for page_number, page in enumerate(reader.pages, start=1):

            text = page.extract_text() or ""

            extracted_pages.append({
                "page_number": page_number,
                "content": text.strip()
            })

        full_text = "\n".join(
            page["content"] for page in extracted_pages
        )

        if not full_text.strip():
            raise ValueError(
                "No extractable text found in PDF."
            )

        return {
            "file_name": path.name,
            "file_type": "PDF",
            "total_pages": len(extracted_pages),
            "total_characters": len(full_text),
            "content": full_text,
            "pages": extracted_pages,
            "status": "SUCCESS"
        }

    def _extract_txt(self, path: Path) -> dict:

        content = path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        if not content.strip():
            raise ValueError(
                "Text document is empty."
            )

        return {
            "file_name": path.name,
            "file_type": "TXT",
            "total_pages": 1,
            "total_characters": len(content),
            "content": content.strip(),
            "pages": [
                {
                    "page_number": 1,
                    "content": content.strip()
                }
            ],
            "status": "SUCCESS"
        }

    def _extract_docx(self, path: Path) -> dict:

        document = Document(str(path))

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        content = "\n".join(paragraphs)

        if not content.strip():
            raise ValueError(
                "No extractable text found in DOCX."
            )

        return {
            "file_name": path.name,
            "file_type": "DOCX",
            "total_pages": None,
            "total_characters": len(content),
            "content": content,
            "pages": [
                {
                    "page_number": 1,
                    "content": content
                }
            ],
            "status": "SUCCESS"
        }
