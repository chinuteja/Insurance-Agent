
import pytest

from app.rag.text_splitter import split_documents


def test_split_documents_creates_multiple_chunks():
    pages = [
        {
            "content": "Insurance policy covers accidental damage. " * 30,
            "metadata": {
                "source": "motor_policy.pdf",
                "page": 1,
            },
        }
    ]

    chunks = split_documents(
        pages,
        chunk_size=100,
        chunk_overlap=20,
    )

    assert len(chunks) > 1


def test_split_documents_preserves_metadata():
    pages = [
        {
            "content": "Flood damage coverage details. " * 20,
            "metadata": {
                "source": "motor_policy.pdf",
                "page": 2,
            },
        }
    ]

    chunks = split_documents(pages)

    assert chunks[0]["metadata"]["source"] == "motor_policy.pdf"
    assert chunks[0]["metadata"]["page"] == 2
    assert chunks[0]["metadata"]["chunk_index"] == 0


def test_split_documents_empty_input():
    with pytest.raises(ValueError):
        split_documents([])


def test_split_documents_invalid_chunk_size():
    pages = [
        {
            "content": "Sample insurance policy text.",
            "metadata": {
                "source": "policy.pdf",
                "page": 1,
            },
        }
    ]

    with pytest.raises(ValueError):
        split_documents(pages, chunk_size=0)


def test_split_documents_invalid_overlap():
    pages = [
        {
            "content": "Sample insurance policy text.",
            "metadata": {
                "source": "policy.pdf",
                "page": 1,
            },
        }
    ]

    with pytest.raises(ValueError):
        split_documents(
            pages,
            chunk_size=100,
            chunk_overlap=100,
        )
