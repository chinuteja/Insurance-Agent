import pytest

from app.rag.vector_store import VectorStoreService
from app.rag.embeddings import EmbeddingService


@pytest.fixture(scope="module")
def embedding_service():
    return EmbeddingService()


@pytest.fixture
def sample_chunks():
    return [
        {
            "content": "Motor insurance covers accidental vehicle damage.",
            "metadata": {
                "source": "motor_policy.pdf",
                "page": 1,
                "chunk_index": 0,
            },
        },
        {
            "content": "Health insurance covers hospitalization and medical expenses.",
            "metadata": {
                "source": "health_policy.pdf",
                "page": 2,
                "chunk_index": 0,
            },
        },
        {
            "content": "Third party insurance covers damage caused to another person.",
            "metadata": {
                "source": "third_party_policy.pdf",
                "page": 3,
                "chunk_index": 0,
            },
        },
    ]


def test_create_vector_store(embedding_service, sample_chunks):
    vector_service = VectorStoreService()

    store = vector_service.create_vector_store(
        sample_chunks,
        embedding_service,
    )

    assert store is not None
    assert vector_service.vector_store is not None


def test_similarity_search_returns_results(
    embedding_service,
    sample_chunks,
):
    vector_service = VectorStoreService()

    vector_service.create_vector_store(
        sample_chunks,
        embedding_service,
    )

    results = vector_service.similarity_search(
        "Does my vehicle insurance cover accidents?",
        k=2,
    )

    assert len(results) == 2
    assert "accidental vehicle damage" in results[0].page_content.lower()


def test_similarity_search_preserves_metadata(
    embedding_service,
    sample_chunks,
):
    vector_service = VectorStoreService()

    vector_service.create_vector_store(
        sample_chunks,
        embedding_service,
    )

    results = vector_service.similarity_search(
        "vehicle accident coverage",
        k=1,
    )

    assert results[0].metadata["source"] == "motor_policy.pdf"
    assert results[0].metadata["page"] == 1


def test_empty_chunks_raise_error(embedding_service):
    vector_service = VectorStoreService()

    with pytest.raises(ValueError):
        vector_service.create_vector_store(
            [],
            embedding_service,
        )


def test_search_before_initialization_raises_error():
    vector_service = VectorStoreService()

    with pytest.raises(ValueError):
        vector_service.similarity_search("vehicle accident")


def test_empty_search_query_raises_error(
    embedding_service,
    sample_chunks,
):
    vector_service = VectorStoreService()

    vector_service.create_vector_store(
        sample_chunks,
        embedding_service,
    )

    with pytest.raises(ValueError):
        vector_service.similarity_search("")


def test_invalid_k_raises_error(
    embedding_service,
    sample_chunks,
):
    vector_service = VectorStoreService()

    vector_service.create_vector_store(
        sample_chunks,
        embedding_service,
    )

    with pytest.raises(ValueError):
        vector_service.similarity_search(
            "vehicle insurance",
            k=0,
        )