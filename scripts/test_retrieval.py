import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.rag.document_loader import load_pdf
from app.rag.text_splitter import split_documents
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStoreService

pdf_path = "data/policies/sample_policy.pdf"

pages = load_pdf(pdf_path)
chunks = split_documents(pages)

embedding_service = EmbeddingService()
vector_store_service = VectorStoreService()

vector_store_service.create_vector_store(
    chunks,
    embedding_service,
)

queries = [
    "Does this policy cover accidental vehicle damage?",
    "What is the premium amount?",
    "Does this policy cover hospitalization?",
]

for query in queries:
    print(f"\nQuery: {query}")

    results = vector_store_service.similarity_search_with_scores(
        query,
        k=3,
    )

    for document, score in results:
        print(f"Score: {score}")
        print(f"Content: {document.page_content}")
        print(f"Metadata: {document.metadata}")