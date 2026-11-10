
from app.rag.ingestion_service import DocumentIngestionService


def main():

    ingestion_service = DocumentIngestionService(
        vector_store_path="data/vector_store"
    )

    result = ingestion_service.ingest_pdf(
        file_path="data/policies/sample_policy.pdf"
    )

    print("\nPolicy ingestion completed:")
    print(result)


if __name__ == "__main__":
    main()
