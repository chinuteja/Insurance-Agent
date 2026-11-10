
from pathlib import Path

import pytest
from docx import Document

from app.document_processing.document_extraction_service import (
    DocumentExtractionService,
)


@pytest.fixture
def extraction_service():
    return DocumentExtractionService()


def test_extract_txt_file(extraction_service, tmp_path):

    file_path = tmp_path / "police_report.txt"

    file_path.write_text(
        "Vehicle accident occurred on 15 October 2026.",
        encoding="utf-8",
    )

    result = extraction_service.extract_text(str(file_path))

    assert result["status"] == "SUCCESS"
    assert result["file_type"] == "TXT"
    assert "Vehicle accident" in result["content"]


def test_extract_docx_file(extraction_service, tmp_path):

    file_path = tmp_path / "repair_estimate.docx"

    document = Document()
    document.add_paragraph("Vehicle registration: TS09AB1234")
    document.add_paragraph("Estimated repair cost: 75000")
    document.save(str(file_path))

    result = extraction_service.extract_text(str(file_path))

    assert result["status"] == "SUCCESS"
    assert result["file_type"] == "DOCX"
    assert "TS09AB1234" in result["content"]


def test_extract_pdf_file(
    extraction_service,
    sample_policy_pdf,
):

    result = extraction_service.extract_text(sample_policy_pdf)

    assert result["status"] == "SUCCESS"
    assert result["file_type"] == "PDF"
    assert result["total_pages"] > 0
    assert "accident damage" in result["content"].lower()


def test_missing_document_raises_error(extraction_service):

    with pytest.raises(FileNotFoundError):
        extraction_service.extract_text(
            "non_existing_document.pdf"
        )


def test_unsupported_document_format(
    extraction_service,
    tmp_path,
):

    file_path = tmp_path / "document.jpg"
    file_path.write_text("sample")

    with pytest.raises(ValueError):
        extraction_service.extract_text(str(file_path))


def test_empty_txt_file_raises_error(
    extraction_service,
    tmp_path,
):

    file_path = tmp_path / "empty.txt"
    file_path.write_text("   ", encoding="utf-8")

    with pytest.raises(ValueError):
        extraction_service.extract_text(str(file_path))
