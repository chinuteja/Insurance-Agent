
from app.rag.vector_store import VectorStoreService


class RetrievalService:

    def __init__(
        self,
        vector_store_service: VectorStoreService,
        max_distance: float = 0.80,
    ):
        if max_distance <= 0:
            raise ValueError("Maximum distance must be greater than zero.")

        self.vector_store_service = vector_store_service
        self.max_distance = max_distance

    def retrieve_documents(self, query: str, k: int = 3) -> dict:

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if k <= 0:
            raise ValueError("k must be greater than zero.")

        results = self.vector_store_service.similarity_search_with_scores(
            query=query,
            k=k,
        )

        retrieved_documents = []

        for document, score in results:
            score = float(score)

            if score <= self.max_distance:
                retrieved_documents.append({
                    "content": document.page_content,
                    "metadata": document.metadata,
                    "score": score,
                })

        if not retrieved_documents:
            return {
                "query": query,
                "results": [],
                "status": "NO_RELEVANT_DOCUMENTS",
                "message": (
                    "No relevant information found in the "
                    "available policy documents."
                ),
            }

        return {
            "query": query,
            "results": retrieved_documents,
            "status": "SUCCESS",
            "message": "Relevant policy documents retrieved successfully.",
        }
