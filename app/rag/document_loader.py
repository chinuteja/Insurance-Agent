
from pathlib import Path

from pypdf import PdfReader


def load_pdf(file_path: str) -> list[dict]:
    """
    Extract text from a PDF file page by page.

    Returns:
        A list containing page content and metadata.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    reader = PdfReader(str(path))

    if reader.is_encrypted:
        raise ValueError("Encrypted PDF files are not supported.")

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append({
                "content": text.strip(),
                "metadata": {
                    "source": path.name,
                    "page": page_number,
                },
            })

    if not pages:
        raise ValueError(
            "No extractable text found in the PDF."
        )

    return pages
