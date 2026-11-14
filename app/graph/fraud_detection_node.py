
from datetime import date

from sqlalchemy.orm import Session

from app.graph.claim_agent_state import ClaimAgentState

from app.repositories.claim_repository import ClaimRepository

from app.services.claim_service import ClaimService
from app.services.policy_service import PolicyService
from app.services.document_service import DocumentService
from app.services.fraud_detection_service import (
    FraudDetectionService,
)

from app.document_processing.document_extraction_service import (
    DocumentExtractionService,
)


def create_fraud_detection_node(db: Session):

    # Initialize repositories and services
    claim_repository = ClaimRepository(db)

    policy_service = PolicyService(db)
    document_service = DocumentService(db)

    document_extraction_service = DocumentExtractionService()

    fraud_detection_service = FraudDetectionService()

    def fraud_detection_node(
        state: ClaimAgentState,
    ) -> dict:

        claim_data = state.get("claim")

        # Safety check: claim must exist
        if not claim_data:
            return {
                "fraud_risk_score": None,
                "fraud_risk_level": None,
                "fraud_findings": [],
                "fraud_recommendation": (
                    "Fraud assessment could not be performed "
                    "because the claim was not found."
                ),
            }

        claim_id = state["claim_id"]

        # Retrieve policy information
        policy = policy_service.get_policy(
            claim_data["policy_id"]
        )

        if policy is None:
            return {
                "fraud_risk_score": None,
                "fraud_risk_level": None,
                "fraud_findings": [],
                "fraud_recommendation": (
                    "Fraud assessment could not be completed "
                    "because the policy record was not found. "
                    "Manual review is required."
                ),
            }

        # Convert incident date into Python date
        incident_date = date.fromisoformat(
            claim_data["incident_date"]
        )

        # Check for duplicate claims
        duplicate_found = (
            claim_repository.find_duplicate_claim(
                policy_id=claim_data["policy_id"],
                incident_date=incident_date,
                claim_type=claim_data["claim_type"],
                exclude_claim_id=claim_id,
            )
        )

        # Count recent claims from the same customer
        recent_claim_count = (
            claim_repository.count_recent_claims(
                customer_id=claim_data["customer_id"],
                reference_date=date.fromisoformat(
                    claim_data["claim_date"]
                ),
                window_days=90,
                exclude_claim_id=claim_id,
            )
        )

        # Extract text from submitted documents
        documents = document_service.get_documents_by_claim(
            claim_id
        )

        document_texts = []
        extraction_errors = []

        for document in documents:

            try:
                extraction_result = (
                    document_extraction_service.extract_text(
                        document.storage_path
                    )
                )

                document_texts.append(
                    extraction_result["content"]
                )

            except Exception as exc:
                extraction_errors.append(
                    f"{document.file_name}: {str(exc)}"
                )

        # Run fraud detection
        result = fraud_detection_service.detect_fraud(
            claim_id=claim_id,
            claim_description=claim_data["description"],
            policy_start_date=policy.start_date,
            incident_date=incident_date,
            duplicate_found=duplicate_found,
            recent_claim_count=recent_claim_count,
            claim_amount=claim_data["claim_amount"],
            document_texts=document_texts,
        )

        # Prepare recommendation
        recommendation = result.recommendation

        if extraction_errors:
            recommendation += (
                " Some documents could not be extracted. "
                "Manual document review is required. "
                + " | ".join(extraction_errors)
            )

        return {
            "fraud_risk_score": result.risk_score,
            "fraud_risk_level": result.risk_level.value,
            "fraud_findings": [
                finding.model_dump(mode="json")
                for finding in result.findings
            ],
            "fraud_recommendation": recommendation,
        }

    return fraud_detection_node
