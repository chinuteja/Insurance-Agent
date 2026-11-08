import pytest
from app.rag.embeddings import EmbeddingService


@pytest.fixture(scope="module")
def embedding_service():
    return EmbeddingService()


def test_generate_embeddings_returns_vectors(embedding_service):
    texts = [
        "Motor insurance covers vehicle damage.",
        "Health insurance covers medical expenses.",
    ]

    embeddings = embedding_service.generate_embeddings(texts)

    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384


def test_generate_embeddings_empty_input(embedding_service):
    with pytest.raises(ValueError):
        embedding_service.generate_embeddings([])


def test_generate_embeddings_rejects_empty_text(embedding_service):
    with pytest.raises(ValueError):
        embedding_service.generate_embeddings([""])


def test_similar_texts_have_higher_similarity(embedding_service):
    texts = [
        "Car insurance protects vehicles against accidents.",
        "Vehicle insurance provides protection against car accidents.",
        "Health insurance covers hospital and medical expenses.",
    ]

    embeddings = embedding_service.generate_embeddings(texts)

    similarity_1 = sum(
        a * b for a, b in zip(embeddings[0], embeddings[1])
    )
    similarity_2 = sum(
        a * b for a, b in zip(embeddings[0], embeddings[2])
    )

    assert similarity_1 > similarity_2