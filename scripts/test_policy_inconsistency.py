
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
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=api_key,
    )

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

    policy_service = PolicyConsistencyService(
        retrieval_service=retrieval_service,
        llm=llm,
    )

    # Scenario: Damage caused by general wear and tear
    document_text = """
    Vehicle inspection report:

    The vehicle has sustained damage due to gradual
    deterioration and general wear and tear.

    The inspection confirms that the damage did not
    result from an accident or collision.
    """

    print("\nStarting policy inconsistency test...")

    result = policy_service.validate_document(
        document_type="VEHICLE_INSPECTION_REPORT",
        document_text=document_text,
        k=3,
    )

    print("\n========== POLICY CONSISTENCY RESULT ==========")

    print(result.model_dump_json(indent=4))

    print("\n========== TEST COMPLETED ==========")


if __name__ == "__main__":
    main()
