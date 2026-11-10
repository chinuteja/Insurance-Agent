import pytest
import numpy as np
from app.rag.vector_store import VectorStoreService
from app.rag.embeddings import EmbeddingService
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

def test_similarity_search_with_scores(
    embedding_service,
    sample_chunks,
):
    vector_service = VectorStoreService()

    vector_service.create_vector_store(
        sample_chunks,
        embedding_service,
    )

    results = vector_service.similarity_search_with_scores(
        "Does vehicle insurance cover accidents?",
        k=2,
    )

    assert len(results) == 2

    document, score = results[0]

    assert isinstance(document.page_content, str)
    # assert isinstance(score, float)
    

    assert isinstance(score, (float, np.floating))
    assert document.metadata["source"] == "motor_policy.pdf"

def test_save_vector_store(
    embedding_service,
    sample_chunks,
    tmp_path,
):
    vector_service = VectorStoreService()

    vector_service.create_vector_store(
        sample_chunks,
        embedding_service,
    )

    save_path = tmp_path / "vector_store"

    vector_service.save_vector_store(str(save_path))

    assert (save_path / "index.faiss").exists()
    assert (save_path / "index.pkl").exists()


def test_load_vector_store(
    embedding_service,
    sample_chunks,
    tmp_path,
):
    original_service = VectorStoreService()

    original_service.create_vector_store(
        sample_chunks,
        embedding_service,
    )

    save_path = tmp_path / "vector_store"

    original_service.save_vector_store(str(save_path))

    # Create a completely new service instance.
    new_service = VectorStoreService()

    new_service.load_vector_store(
        str(save_path),
        embedding_service,
    )

    results = new_service.similarity_search(
        "Does vehicle insurance cover accidents?",
        k=1,
    )

    assert len(results) == 1
    assert "accidental vehicle damage" in results[0].page_content.lower()


def test_save_uninitialized_vector_store_raises_error(tmp_path):
    vector_service = VectorStoreService()

    with pytest.raises(ValueError):
        vector_service.save_vector_store(
            str(tmp_path / "vector_store")
        )