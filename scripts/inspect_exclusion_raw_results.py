
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStoreService


def main():

    embedding_service = EmbeddingService()
    vector_store_service = VectorStoreService()

    vector_store_service.load_vector_store(
        directory="data/vector_store",
        embedding_service=embedding_service,
    )

    document_type = "VEHICLE_INSPECTION_REPORT"

    document_text = """
    Vehicle inspection report:

    The vehicle has sustained damage due to gradual
    deterioration and general wear and tear.

    The inspection confirms that the damage did not
    result from an accident or collision.
    """

    query = (
        f"Insurance policy coverage, exclusions, limitations, "
        f"and conditions relevant to {document_type}. "
        f"Find policy clauses that support or contradict the "
        f"following document information: "
        f"{document_text[:6000]}"
    )

    print("\nEXACT POLICY CONSISTENCY QUERY:")
    print(query)

    results = vector_store_service.similarity_search_with_scores(
        query=query,
        k=5,
    )

    print("\nRAW RETRIEVAL RESULTS:")

    for index, (document, score) in enumerate(results, start=1):

        print(f"\nRESULT {index}")
        print("DISTANCE:", float(score))
        print("CONTENT:", document.page_content)
        print("METADATA:", document.metadata)


if __name__ == "__main__":
    main()
