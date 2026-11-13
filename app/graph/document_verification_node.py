
from sqlalchemy.orm import Session

from app.graph.claim_agent_state import ClaimAgentState
from app.services.document_verification_service import (
    DocumentVerificationService,
)
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStoreService
from app.rag.retrieval_service import RetrievalService
from app.services.policy_consistency_service import (
    PolicyConsistencyService,
)
from app.llm import create_llm


def create_document_verification_node(db: Session):

    # Initialize embedding service
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

    # Initialize LLM
    llm = create_llm()

    # Initialize policy consistency service
    policy_consistency_service = PolicyConsistencyService(
        retrieval_service=retrieval_service,
        llm=llm,
    )

    # Initialize document verification service
    document_verification_service = DocumentVerificationService(
        db=db,
        policy_consistency_service=policy_consistency_service,
    )

    def document_verification_node(
        state: ClaimAgentState,
    ) -> dict:

        claim_id = state["claim_id"]

        result = (
            document_verification_service.verify_claim_documents(
                claim_id=claim_id,
            )
        )

        return {
            "document_verification_status": (
                result.overall_status.value
            ),
            "document_verification_results": [
                document.model_dump(mode="json")
                for document in result.documents
            ],
            "missing_documents": result.missing_documents,
            "document_inconsistencies": result.inconsistencies,
            "document_recommendation": result.recommendation,
        }

    return document_verification_node
