from app.rag.ingestion_service import DocumentIngestionService


def test_ingest_pdf(sample_policy_pdf):
    ingestion_service = DocumentIngestionService()

    result = ingestion_service.ingest_pdf(sample_policy_pdf)

    assert result["status"] == "SUCCESS"
    assert result["total_pages"] > 0
    assert result["total_chunks"] > 0
    assert result["embedding_dimensions"] == 384
    assert result["file_name"] == "sample_policy.pdf"