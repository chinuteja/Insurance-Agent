
from pathlib import Path

import pytest
from pypdf import PdfWriter
from pypdf.generic import (
    DictionaryObject,
    NameObject,
    TextStringObject,
)

from app.rag.document_loader import load_pdf


def create_sample_pdf(file_path: Path):
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)

    # Add a simple text content stream to the PDF page.
    content = b"BT /F1 12 Tf 40 200 Td (Insurance policy covers accident damage) Tj ET"

    from pypdf.generic import DecodedStreamObject

    stream = DecodedStreamObject()
    stream.set_data(content)

    page[NameObject("/Contents")] = stream

    font = DictionaryObject()
    font.update({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })

    resources = DictionaryObject()
    fonts = DictionaryObject()
    fonts[NameObject("/F1")] = font
    resources[NameObject("/Font")] = fonts
    page[NameObject("/Resources")] = resources

    with open(file_path, "wb") as file:
        writer.write(file)


def test_load_pdf_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_pdf("missing_policy.pdf")


def test_load_pdf_invalid_extension(tmp_path):
    file_path = tmp_path / "policy.txt"
    file_path.write_text("Sample policy")

    with pytest.raises(ValueError):
        load_pdf(str(file_path))


def test_load_pdf_empty_document(tmp_path):
    file_path = tmp_path / "empty.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    with open(file_path, "wb") as file:
        writer.write(file)

    with pytest.raises(ValueError):
        load_pdf(str(file_path))


def test_load_pdf_extracts_text_and_page_metadata(tmp_path):
    file_path = tmp_path / "sample_policy.pdf"
    create_sample_pdf(file_path)

    pages = load_pdf(str(file_path))

    assert len(pages) == 1
    assert "Insurance policy covers accident damage" in pages[0]["content"]
    assert pages[0]["metadata"]["source"] == "sample_policy.pdf"
    assert pages[0]["metadata"]["page"] == 1
