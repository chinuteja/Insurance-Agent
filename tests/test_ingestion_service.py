from app.rag.ingestion_service import DocumentIngestionService


def test_ingest_pdf(sample_policy_pdf):
    ingestion_service = DocumentIngestionService()

    result = ingestion_service.ingest_pdf(sample_policy_pdf)

    assert result["status"] == "SUCCESS"
    assert result["total_pages"] > 0
    assert result["total_chunks"] > 0
    assert result["embedding_dimensions"] == 384
    assert result["file_name"] == "sample_policy.pdf"

def test_load_existing_vector_store(sample_policy_pdf, tmp_path):
    from app.rag.ingestion_service import DocumentIngestionService

    vector_store_path = str(tmp_path / "vector_store")

    # First run: ingest PDF and save FAISS index.
    ingestion_service = DocumentIngestionService(
        vector_store_path=vector_store_path
    )
    ingestion_service.ingest_pdf(sample_policy_pdf)

    # Simulate application restart with a new service instance.
    restarted_service = DocumentIngestionService(
        vector_store_path=vector_store_path
    )

    # Load saved index without ingesting the PDF again.
    vector_store = restarted_service.load_existing_vector_store()

    # Search the previously saved index.
    results = vector_store.similarity_search(
        "Does this policy cover accidental vehicle damage?",
        k=1,
    )

    assert len(results) == 1
    assert "accident damage" in results[0].page_content.lower()
