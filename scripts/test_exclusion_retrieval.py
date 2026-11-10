
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

    queries = [
        "Is general wear and tear excluded?",
        "What exclusions are mentioned in this insurance policy?",
        "Does the policy cover gradual deterioration of a vehicle?",
    ]

    for query in queries:

        print("\n" + "=" * 70)
        print("QUERY:", query)

        result = retrieval_service.retrieve_documents(
            query=query,
            k=5,
        )

        print("STATUS:", result["status"])

        for item in result["results"]:
            print("\nDISTANCE:", item["score"])
            print("CONTENT:", item["content"])
            print("METADATA:", item["metadata"])


if __name__ == "__main__":
    main()
