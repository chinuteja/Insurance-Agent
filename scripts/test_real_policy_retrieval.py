
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStoreService
from app.rag.retrieval_service import RetrievalService


def main():

    embedding_service = EmbeddingService()

    vector_store_service = VectorStoreService()

    vector_store_service.load_vector_store(
        "data/vector_store",
        embedding_service,
    )

    retrieval_service = RetrievalService(
        vector_store_service=vector_store_service,
        max_distance=0.80,
    )

    queries = [
        "Does this policy cover accidental vehicle damage?",
        "Is flood damage covered under this policy?",
        "Is general wear and tear excluded?",
    ]

    for query in queries:

        print("\n" + "=" * 70)
        print("QUERY:", query)

        # Get raw FAISS distance before threshold filtering.
        raw_results = (vector_store_service.similarity_search_with_scores(
        query=query,k=3,))

        for index, (document, score) in enumerate(raw_results, start=1):
            print(f"\nRAW RESULT {index}")
            print("DISTANCE:", float(score))
            print("CONTENT:", document.page_content)
            print("METADATA:", document.metadata)
        

        # Get filtered retrieval result.
        result = retrieval_service.retrieve_documents(
            query=query,
            k=3,
        )

        print("FILTERED STATUS:", result["status"])

        for item in result["results"]:

            print("CONTENT:", item["content"])
            print("METADATA:", item["metadata"])
            print("DISTANCE:", item["score"])


if __name__ == "__main__":
    main()
