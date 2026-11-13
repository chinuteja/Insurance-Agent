
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

    query = """
    Insurance policy coverage, exclusions, limitations,
    and conditions relevant to vehicle inspection.
    The vehicle damage resulted from gradual deterioration
    and general wear and tear, not an accident.
    """

    keywords = [
        "wear and tear",
        "gradual deterioration",
        "exclusion",
    ]

    print("\nStarting combined retrieval test...")

    result = retrieval_service.retrieve_policy_evidence(
        query=query,
        keywords=keywords,
        k=5,
    )

    print("\n========== COMBINED RETRIEVAL RESULT ==========")

    print("STATUS:", result["status"])
    print("MESSAGE:", result["message"])
    print("TOTAL DOCUMENTS:", len(result["results"]))

    for index, document in enumerate(result["results"], start=1):

        print(f"\nRESULT {index}")
        print("CONTENT:", document["content"])
        print("METADATA:", document["metadata"])
        print("DISTANCE:", document["score"])
        print("RETRIEVAL METHODS:", document["retrieval_methods"])
        print("MATCHED KEYWORDS:", document["matched_keywords"])

    print("\n========== TEST COMPLETED ==========")


if __name__ == "__main__":
    main()
