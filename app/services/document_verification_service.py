
from pathlib import Path

from sqlalchemy.orm import Session

from app.services.claim_service import ClaimService
from app.services.document_service import DocumentService
from app.document_processing.document_extraction_service import (
    DocumentExtractionService,
)
from app.schemas.document_verification_schema import (
    DocumentVerificationStatus,
    OverallVerificationStatus,
    DocumentIssue,
    DocumentVerificationResult,
    ClaimDocumentVerificationResponse,
)


class DocumentVerificationService:

    REQUIRED_DOCUMENTS = [
        "POLICE_REPORT",
        "VEHICLE_PHOTOS",
        "REPAIR_ESTIMATE",
        "DRIVING_LICENCE",
        "VEHICLE_REGISTRATION",
        "INSURANCE_POLICY",
    ]

    def __init__(self, db: Session):

        self.claim_service = ClaimService(db)
        self.document_service = DocumentService(db)
        self.extraction_service = DocumentExtractionService()

    def verify_claim_documents(
        self,
        claim_id: str,
    ) -> ClaimDocumentVerificationResponse:

        # Step 1: Retrieve claim details.
        claim = self.claim_service.get_claim(claim_id)

        # Step 2: Retrieve submitted documents.
        submitted_documents = (
            self.document_service.get_documents_by_claim(claim_id)
        )

        submitted_types = {
            document.document_type.strip().upper()
            for document in submitted_documents
        }

        verification_results = []
        missing_documents = []
        inconsistencies = []

        # Step 3: Check all required document types.
        for document_type in self.REQUIRED_DOCUMENTS:

            matching_documents = [
                document
                for document in submitted_documents
                if document.document_type.strip().upper()
                == document_type
            ]

            if not matching_documents:

                missing_documents.append(document_type)

                verification_results.append(
                    DocumentVerificationResult(
                        document_type=document_type,
                        status=DocumentVerificationStatus.MISSING,
                        issues=[
                            DocumentIssue(
                                issue_type="MISSING_DOCUMENT",
                                description=(
                                    f"{document_type} was not submitted."
                                ),
                            )
                        ],
                    )
                )

                continue

            # Step 4: Extract text from submitted files.
            for document in matching_documents:

                try:
                    extraction_result = (
                        self.extraction_service.extract_text(
                            document.storage_path
                        )
                    )

                    verification_results.append(
                        DocumentVerificationResult(
                            document_type=document_type,
                            status=DocumentVerificationStatus.NEEDS_REVIEW,
                            extracted_fields={
                                "file_name": extraction_result["file_name"],
                                "file_type": extraction_result["file_type"],
                                "total_characters": (
                                    extraction_result["total_characters"]
                                ),
                            },
                            issues=[
                                DocumentIssue(
                                    issue_type="CONTENT_VERIFICATION_PENDING",
                                    description=(
                                        "Text extraction succeeded. "
                                        "Content and claim details "
                                        "still require verification."
                                    ),
                                )
                            ],
                        )
                    )

                except Exception as error:

                    inconsistencies.append(
                        f"{document_type}: Unable to extract document text."
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

        # Step 5: Flag unsupported document types.
        for document in submitted_documents:

            document_type = document.document_type.strip().upper()

            if document_type not in self.REQUIRED_DOCUMENTS:
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

        # Step 6: Determine overall verification status.
        if missing_documents:
            overall_status = OverallVerificationStatus.INCOMPLETE

            recommendation = (
                "Request the missing documents before proceeding "
                "with verification."
            )

        elif any(
            result.status in (
                DocumentVerificationStatus.INVALID,
                DocumentVerificationStatus.NEEDS_REVIEW,
            )
            for result in verification_results
        ):
            overall_status = OverallVerificationStatus.NEEDS_REVIEW

            recommendation = (
                "Review the extracted documents and complete "
                "content validation."
            )

        else:
            overall_status = OverallVerificationStatus.VERIFIED

            recommendation = (
                "All required documents passed the current checks."
            )

        # Step 7: Return structured response.
        return ClaimDocumentVerificationResponse(
            claim_id=claim.claim_id,
            overall_status=overall_status,
            documents=verification_results,
            missing_documents=missing_documents,
            inconsistencies=inconsistencies,
            recommendation=recommendation,
        )
