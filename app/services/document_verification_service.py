
from sqlalchemy.orm import Session

from app.document_processing.document_extraction_service import (
    DocumentExtractionService,
)
from app.document_processing.document_requirements import (
    DocumentRequirement,
    get_document_requirements,
)
from app.schemas.document_verification_schema import (
    ClaimDocumentVerificationResponse,
    DocumentIssue,
    DocumentVerificationResult,
    DocumentVerificationStatus,
    OverallVerificationStatus,
)
from app.schemas.policy_consistency_schema import PolicyConsistencyStatus
from app.services.claim_service import ClaimService
from app.services.document_service import DocumentService


class DocumentVerificationService:
    DOCUMENT_TYPES = [  # noqa: RUF012
    "POLICE_REPORT",
    "VEHICLE_PHOTOS",
    "REPAIR_ESTIMATE",
    "DRIVING_LICENCE",
    "VEHICLE_REGISTRATION",
    "INSURANCE_POLICY",
]
    REQUIRED_DOCUMENTS = DOCUMENT_TYPES

    
    def __init__(
        self,
        db: Session,
        policy_consistency_service=None,
    ):
        self.claim_service = ClaimService(db)
        self.document_service = DocumentService(db)
        self.extraction_service = DocumentExtractionService()
        self.policy_consistency_service = policy_consistency_service

    def verify_claim_documents(
        self,
        claim_id: str,
    ) -> ClaimDocumentVerificationResponse:

        # Step 1: Retrieve claim details.
        claim = self.claim_service.get_claim(claim_id)

        # Step 2: Get document requirements for this claim type.
        requirements = get_document_requirements(claim.claim_type)

        # Step 3: Retrieve submitted documents.
        submitted_documents = (
            self.document_service.get_documents_by_claim(claim_id)
        )

        verification_results = []
        missing_documents = []
        inconsistencies = []

        # Normalize submitted document types.
        submitted_by_type = {}

        for document in submitted_documents:
            document_type = document.document_type.strip().upper()

            submitted_by_type.setdefault(
                document_type,
                [],
            ).append(document)

        # Step 4: Process documents according to claim requirements.
        for document_type, requirement in requirements.items():

            matching_documents = submitted_by_type.get(
                document_type,
                [],
            )

            # Required document missing.
            if (
                requirement == DocumentRequirement.REQUIRED
                and not matching_documents
            ):
                missing_documents.append(document_type)

                verification_results.append(
                    DocumentVerificationResult(
                        document_type=document_type,
                        status=DocumentVerificationStatus.MISSING,
                        issues=[
                            DocumentIssue(
                                issue_type="MISSING_DOCUMENT",
                                description=(
                                    f"{document_type} is required "
                                    f"for a {claim.claim_type} claim "
                                    "but was not submitted."
                                ),
                            )
                        ],
                    )
                )

                continue

            # Conditional document missing.
            if (
                requirement == DocumentRequirement.CONDITIONAL
                and not matching_documents
            ):
                verification_results.append(
                    DocumentVerificationResult(
                        document_type=document_type,
                        status=DocumentVerificationStatus.NEEDS_REVIEW,
                        issues=[
                            DocumentIssue(
                                issue_type="CONDITIONAL_DOCUMENT_REVIEW",
                                description=(
                                    f"{document_type} was not submitted. "
                                    "Its necessity depends on the "
                                    "claim circumstances."
                                ),
                            )
                        ],
                    )
                )

                continue

            # Documents marked NOT_REQUIRED are ignored.
            if requirement == DocumentRequirement.NOT_REQUIRED:
                continue

            # Step 5: Extract and verify submitted documents.
            for document in matching_documents:

                try:
                    extraction_result = (
                        self.extraction_service.extract_text(
                            document.storage_path
                        )
                    )

                    extracted_fields = {
                        "file_name": extraction_result["file_name"],
                        "file_type": extraction_result["file_type"],
                        "total_characters": (
                            extraction_result["total_characters"]
                        ),
                    }

                    issues = [
                        DocumentIssue(
                            issue_type="CONTENT_VERIFICATION_PENDING",
                            description=(
                                "Text extraction succeeded. "
                                "Claim details still require verification."
                            ),
                        )
                    ]

                    # Step 6: Check consistency against policy evidence.
                    if self.policy_consistency_service is not None:

                        policy_result = (
                            self.policy_consistency_service.validate_document(
                                document_type=document_type,
                                document_text=extraction_result["content"],
                            )
                        )

                        extracted_fields["policy_consistency"] = (
                            policy_result.model_dump(mode="json")
                        )

                        if (
                            policy_result.overall_status
                            == PolicyConsistencyStatus.INCONSISTENT
                        ):
                            inconsistencies.append(
                                f"{document_type}: "
                                "Policy inconsistency detected."
                            )

                            issues.append(
                                DocumentIssue(
                                    issue_type="POLICY_INCONSISTENCY",
                                    description=(
                                        policy_result.recommendation
                                    ),
                                )
                            )

                        elif policy_result.overall_status in (
                            PolicyConsistencyStatus.NEEDS_REVIEW,
                            PolicyConsistencyStatus.INSUFFICIENT_EVIDENCE,
                        ):
                            issues.append(
                                DocumentIssue(
                                    issue_type="POLICY_REVIEW_REQUIRED",
                                    description=(
                                        policy_result.recommendation
                                    ),
                                )
                            )

                    # Extraction succeeded, but verification is not complete.
                    verification_results.append(
                        DocumentVerificationResult(
                            document_type=document_type,
                            status=DocumentVerificationStatus.NEEDS_REVIEW,
                            extracted_fields=extracted_fields,
                            issues=issues,
                        )
                    )

                except Exception as error:

                    inconsistencies.append(
                        f"{document_type}: "
                        "Unable to extract or verify document."
                    )

                    verification_results.append(
                        DocumentVerificationResult(
                            document_type=document_type,
                            status=DocumentVerificationStatus.INVALID,
                            issues=[
                                DocumentIssue(
                                    issue_type="EXTRACTION_FAILED",
                                    description=str(error),
                                )
                            ],
                        )
                    )

        # Step 7: Identify unsupported submitted document types.
        supported_document_types = set(self.DOCUMENT_TYPES)

        for document_type, matching_documents in submitted_by_type.items():

            if document_type not in supported_document_types:

                for _ in matching_documents:
                    verification_results.append(
                        DocumentVerificationResult(
                            document_type=document_type,
                            status=DocumentVerificationStatus.NEEDS_REVIEW,
                            issues=[
                                DocumentIssue(
                                    issue_type="UNSUPPORTED_DOCUMENT_TYPE",
                                    description=(
                                        "This document type is not part "
                                        "of the current verification checklist."
                                    ),
                                )
                            ],
                        )
                    )

        # Step 8: Determine overall verification status.
        if missing_documents:

            overall_status = OverallVerificationStatus.INCOMPLETE

            recommendation = (
                "Request the missing mandatory documents before "
                "proceeding with verification."
            )

        elif any(
            result.status == DocumentVerificationStatus.INVALID
            for result in verification_results
        ):

            overall_status = OverallVerificationStatus.NEEDS_REVIEW

            recommendation = (
                "One or more documents could not be extracted or verified. "
                "Manual review is required."
            )

        elif any(
            result.status == DocumentVerificationStatus.NEEDS_REVIEW
            for result in verification_results
        ):

            overall_status = OverallVerificationStatus.NEEDS_REVIEW

            recommendation = (
                "Review the submitted documents, conditional requirements, "
                "and outstanding content or policy checks."
            )

        else:

            overall_status = OverallVerificationStatus.VERIFIED

            recommendation = (
                "All applicable document requirements passed "
                "the current checks."
            )

        # Step 9: Return structured verification response.
        return ClaimDocumentVerificationResponse(
            claim_id=claim.claim_id,
            overall_status=overall_status,
            documents=verification_results,
            missing_documents=missing_documents,
            inconsistencies=inconsistencies,
            recommendation=recommendation,
        )
