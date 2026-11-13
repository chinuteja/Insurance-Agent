
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStoreService
from app.rag.retrieval_service import RetrievalService


def main():

    embedding_service = EmbeddingService()

    vector_store_service = VectorStoreService()

    vector_store_service.load_vector_store(
        directory="data/vector_store",
        embedding_service=embedding_service,
    )

    retrieval_service = RetrievalService(
        vector_store_service=vector_store_service,
        max_distance=0.80,
    )

    keywords = [
        "wear and tear",
        "gradual deterioration",
        "exclusion",
    ]

    print("\nStarting keyword-based policy retrieval...")

    result = retrieval_service.retrieve_by_keywords(
        keywords=keywords
    )

    print("\n========== KEYWORD RETRIEVAL RESULT ==========")

    print("STATUS:", result["status"])
    print("MESSAGE:", result["message"])

    for index, document in enumerate(result["results"], start=1):

        print(f"\nRESULT {index}")
        print("CONTENT:", document["content"])
        print("METADATA:", document["metadata"])
        print("MATCHED KEYWORDS:", document["matched_keywords"])

    print("\n========== TEST COMPLETED ==========")


if __name__ == "__main__":
    main()
