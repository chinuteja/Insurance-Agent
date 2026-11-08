from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


class VectorStoreService:

    def __init__(self):
        self.vector_store = None

    def create_vector_store(
        self,
        chunks: list[dict],
        embedding_service,
    ):
        if not chunks:
            raise ValueError("No chunks provided for vector storage.")

        documents = [
            Document(
                page_content=chunk["content"],
                metadata=chunk["metadata"],
            )
            for chunk in chunks
        ]

        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=embedding_service.model,
        )

        return self.vector_store

    def similarity_search(
        self,
        query: str,
        k: int = 3,
    ) -> list[Document]:

        if self.vector_store is None:
            raise ValueError("Vector store has not been initialized.")

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if k <= 0:
            raise ValueError("k must be greater than zero.")

        return self.vector_store.similarity_search(
            query,
            k=k,
        )