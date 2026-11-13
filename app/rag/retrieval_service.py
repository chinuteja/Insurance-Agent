
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
                    "retrieval_methods": ["semantic"],
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

    def retrieve_by_keywords(
        self,
        keywords: list[str],
    ) -> dict:

        if not keywords or not any(
            keyword.strip() for keyword in keywords
        ):
            raise ValueError("At least one valid keyword is required.")

        if self.vector_store_service.vector_store is None:
            raise ValueError("Vector store has not been initialized.")

        all_documents = (
            self.vector_store_service.vector_store.docstore._dict.values()
        )

        retrieved_documents = []
        seen_documents = set()

        normalized_keywords = [
            keyword.strip().lower()
            for keyword in keywords
            if keyword.strip()
        ]

        for document in all_documents:

            content = document.page_content.lower()

            matched_keywords = [
                keyword
                for keyword in normalized_keywords
                if keyword in content
            ]

            if not matched_keywords:
                continue

            metadata = document.metadata

            document_id = (
                metadata.get("source"),
                metadata.get("page"),
                metadata.get("chunk_index"),
                document.page_content,
            )

            if document_id in seen_documents:
                continue

            seen_documents.add(document_id)

            retrieved_documents.append({
                "content": document.page_content,
                "metadata": metadata,
                "score": None,
                "matched_keywords": matched_keywords,
                "retrieval_methods": ["keyword"],
            })

        return {
            "results": retrieved_documents,
            "status": (
                "SUCCESS" if retrieved_documents
                else "NO_RELEVANT_DOCUMENTS"
            ),
            "message": (
                "Keyword-based policy evidence retrieved successfully."
                if retrieved_documents
                else "No policy clauses matched the supplied keywords."
            ),
        }

    def retrieve_policy_evidence(
        self,
        query: str,
        keywords: list[str],
        k: int = 3,
    ) -> dict:

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if k <= 0:
            raise ValueError("k must be greater than zero.")

        # Step 1: Semantic retrieval
        semantic_result = self.retrieve_documents(
            query=query,
            k=k,
        )

        # Step 2: Keyword retrieval
        keyword_result = self.retrieve_by_keywords(
            keywords=keywords,
        )

        # Step 3: Merge and deduplicate
        combined_documents = {}

        for document in semantic_result["results"]:

            metadata = document["metadata"]

            document_id = (
                metadata.get("source"),
                metadata.get("page"),
                metadata.get("chunk_index"),
                document["content"],
            )

            combined_documents[document_id] = {
                **document,
                "retrieval_methods": ["semantic"],
                "matched_keywords": [],
            }

        for document in keyword_result["results"]:

            metadata = document["metadata"]

            document_id = (
                metadata.get("source"),
                metadata.get("page"),
                metadata.get("chunk_index"),
                document["content"],
            )

            if document_id in combined_documents:

                existing = combined_documents[document_id]

                existing["retrieval_methods"].append("keyword")

                existing["matched_keywords"] = (
                    document["matched_keywords"]
                )

            else:

                combined_documents[document_id] = {
                    **document,
                    "retrieval_methods": ["keyword"],
                }

        # Step 4: Prepare final response
        results = list(combined_documents.values())

        return {
            "query": query,
            "results": results,
            "status": (
                "SUCCESS" if results
                else "NO_RELEVANT_DOCUMENTS"
            ),
            "message": (
                "Combined policy evidence retrieved successfully."
                if results
                else "No relevant policy evidence found."
            ),
        }
