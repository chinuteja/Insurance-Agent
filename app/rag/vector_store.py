from pathlib import Path

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

    def similarity_search_with_scores(
        self,
        query: str,
        k: int = 3,
    ) -> list[tuple[Document, float]]:

        if self.vector_store is None:
            raise ValueError("Vector store has not been initialized.")

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if k <= 0:
            raise ValueError("k must be greater than zero.")

        return self.vector_store.similarity_search_with_score(
            query,
            k=k,
        )

    def save_vector_store(self, directory: str):

        if self.vector_store is None:
            raise ValueError("No vector store available to save.")

        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)

        self.vector_store.save_local(str(path))

    def load_vector_store(
        self,
        directory: str,
        embedding_service,
    ):

        path = Path(directory)

        if not path.exists():
            raise FileNotFoundError(
                f"Vector store directory not found: {directory}"
            )

        index_file = path / "index.faiss"
        metadata_file = path / "index.pkl"

        if not index_file.exists() or not metadata_file.exists():
            raise FileNotFoundError(
                "FAISS index files are missing."
            )

        self.vector_store = FAISS.load_local(
            str(path),
            embeddings=embedding_service.model,
            allow_dangerous_deserialization=True,
        )

        return self.vector_store