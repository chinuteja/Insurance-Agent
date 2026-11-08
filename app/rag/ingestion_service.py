from app.rag.document_loader import load_pdf
from app.rag.text_splitter import split_documents
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStoreService


class DocumentIngestionService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store_service = VectorStoreService()

    def ingest_pdf(self, file_path: str) -> dict:
        # Step 1: Extract PDF text
        pages = load_pdf(file_path)

        # Step 2: Split text into chunks
        chunks = split_documents(pages)

        # Step 3: Generate embeddings
        texts = [chunk["content"] for chunk in chunks]

        embeddings = self.embedding_service.generate_embeddings(texts)

        # Step 4: Create FAISS vector store
        self.vector_store_service.create_vector_store(
            chunks,
            self.embedding_service,
        )

        return {
            "file_name": pages[0]["metadata"]["source"],
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "embedding_dimensions": len(embeddings[0]),
            "status": "SUCCESS",
        }