
from enum import Enum


class DocumentRequirement(str, Enum):
    REQUIRED = "REQUIRED"
    CONDITIONAL = "CONDITIONAL"
    NOT_REQUIRED = "NOT_REQUIRED"


DOCUMENT_REQUIREMENTS_BY_CLAIM_TYPE = {
    "ACCIDENT": {
        "POLICE_REPORT": DocumentRequirement.REQUIRED,
        "VEHICLE_PHOTOS": DocumentRequirement.REQUIRED,
        "REPAIR_ESTIMATE": DocumentRequirement.REQUIRED,
        "DRIVING_LICENCE": DocumentRequirement.REQUIRED,
        "VEHICLE_REGISTRATION": DocumentRequirement.REQUIRED,
        "INSURANCE_POLICY": DocumentRequirement.REQUIRED,
    },
    "THEFT": {
        "POLICE_REPORT": DocumentRequirement.REQUIRED,
        "VEHICLE_PHOTOS": DocumentRequirement.CONDITIONAL,
        "REPAIR_ESTIMATE": DocumentRequirement.NOT_REQUIRED,
        "DRIVING_LICENCE": DocumentRequirement.NOT_REQUIRED,
        "VEHICLE_REGISTRATION": DocumentRequirement.REQUIRED,
        "INSURANCE_POLICY": DocumentRequirement.REQUIRED,
    },
    "NATURAL_DISASTER": {
        "POLICE_REPORT": DocumentRequirement.CONDITIONAL,
        "VEHICLE_PHOTOS": DocumentRequirement.REQUIRED,
        "REPAIR_ESTIMATE": DocumentRequirement.REQUIRED,
        "DRIVING_LICENCE": DocumentRequirement.REQUIRED,
        "VEHICLE_REGISTRATION": DocumentRequirement.REQUIRED,
        "INSURANCE_POLICY": DocumentRequirement.REQUIRED,
    },
}


def get_document_requirements(claim_type: str) -> dict:
    normalized_claim_type = claim_type.strip().upper()

    requirements = DOCUMENT_REQUIREMENTS_BY_CLAIM_TYPE.get(
        normalized_claim_type
    )

    if requirements is None:
        raise ValueError(
            f"Unsupported claim type: {claim_type}"
        )

    return requirements.copy()
