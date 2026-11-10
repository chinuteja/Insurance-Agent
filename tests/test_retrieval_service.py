import pytest

from app.rag.retrieval_service import RetrievalService
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
    ]


@pytest.fixture
def retrieval_service(embedding_service, sample_chunks):
    vector_store_service = VectorStoreService()

    vector_store_service.create_vector_store(
        sample_chunks,
        embedding_service,
    )

    return RetrievalService(
        vector_store_service,
        max_distance=0.80,
    )


def test_retrieve_documents_returns_success(retrieval_service):
    response = retrieval_service.retrieve_documents(
        "Does vehicle insurance cover accidents?",
        k=2,
    )

    assert response["status"] == "SUCCESS"
    assert len(response["results"]) > 0


def test_retrieve_documents_returns_expected_fields(retrieval_service):
    response = retrieval_service.retrieve_documents(
        "vehicle accident coverage",
        k=1,
    )

    result = response["results"][0]

    assert "content" in result
    assert "metadata" in result
    assert "score" in result


def test_retrieve_documents_preserves_metadata(retrieval_service):
    response = retrieval_service.retrieve_documents(
        "vehicle accident coverage",
        k=1,
    )

    result = response["results"][0]

    assert result["metadata"]["source"] == "motor_policy.pdf"
    assert result["metadata"]["page"] == 1


def test_retrieve_documents_empty_query(retrieval_service):
    with pytest.raises(ValueError):
        retrieval_service.retrieve_documents("")


def test_retrieve_documents_invalid_k(retrieval_service):
    with pytest.raises(ValueError):
        retrieval_service.retrieve_documents(
            "vehicle insurance",
            k=0,
        )


def test_retrieval_returns_no_relevant_documents(retrieval_service):
    response = retrieval_service.retrieve_documents(
        "What is the premium amount?",
        k=2,
    )

    assert response["status"] == "NO_RELEVANT_DOCUMENTS"
    assert response["results"] == []
    assert "No relevant information found" in response["message"]


def test_retrieval_response_contains_original_query(retrieval_service):
    query = "Does my policy cover accidents?"

    response = retrieval_service.retrieve_documents(query)

    assert response["query"] == query


def test_retrieval_from_persisted_vector_store(
    sample_policy_pdf,
    tmp_path,
):
    from app.rag.ingestion_service import DocumentIngestionService
    from app.rag.retrieval_service import RetrievalService

    vector_store_path = str(tmp_path / "vector_store")

    # First application run: ingest and save the PDF.
    ingestion_service = DocumentIngestionService(
        vector_store_path=vector_store_path
    )
    ingestion_service.ingest_pdf(sample_policy_pdf)

    # Simulate application restart.
    restarted_service = DocumentIngestionService(
        vector_store_path=vector_store_path
    )

    vector_store = restarted_service.load_existing_vector_store()

    # Create retrieval service using the loaded FAISS index.
    retrieval_service = RetrievalService(
        vector_store_service=vector_store
    )

    response = retrieval_service.retrieve_documents(
        query="Does this policy cover accidental vehicle damage?",
        k=3,
    )
    
    assert response["status"] == "SUCCESS"
    assert len(response["results"]) > 0
    assert any(
        "accident damage" in result["content"].lower()
        for result in response["results"]
    )
