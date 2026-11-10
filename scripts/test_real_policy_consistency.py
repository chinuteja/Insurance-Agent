
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStoreService
from app.rag.retrieval_service import RetrievalService
from app.services.policy_consistency_service import (
    PolicyConsistencyService,
)


def main():
    # Load environment variables
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

    # Initialize the LLM
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=api_key,
    )

    # Initialize embeddings
    embedding_service = EmbeddingService()

    # Load existing FAISS vector store
    vector_store_service = VectorStoreService()

    vector_store_service.load_vector_store(
        directory="data/vector_store",
        embedding_service=embedding_service,
    )

    # Initialize retrieval service
    retrieval_service = RetrievalService(
        vector_store_service=vector_store_service,
        max_distance=0.80,
    )

    # Initialize policy consistency service
    policy_service = PolicyConsistencyService(
        retrieval_service=retrieval_service,
        llm=llm,
    )

    # Sample submitted document
    document_text = """
    The vehicle sustained accidental collision damage.
    The repair estimate records damage to the front bumper
    and headlight. The damage occurred during a road accident.
    """

    print("\nStarting real LLM policy consistency test...")

    result = policy_service.validate_document(
        document_type="REPAIR_ESTIMATE",
        document_text=document_text,
        k=3,
    )

    print("\n========== POLICY CONSISTENCY RESULT ==========")

    print(result.model_dump_json(indent=4))

    print("\n========== TEST COMPLETED ==========")


if __name__ == "__main__":
    main()
