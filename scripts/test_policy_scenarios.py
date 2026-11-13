
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

    # Initialize LLM
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=api_key,
    )

    # Initialize embeddings
    embedding_service = EmbeddingService()

    # Load FAISS vector store
    vector_store_service = VectorStoreService()

    vector_store_service.load_vector_store(
        directory="data/vector_store",
        embedding_service=embedding_service,
    )

    # Initialize retrieval
    retrieval_service = RetrievalService(
        vector_store_service=vector_store_service,
        max_distance=0.80,
    )

    # Initialize policy consistency service
    policy_service = PolicyConsistencyService(
        retrieval_service=retrieval_service,
        llm=llm,
    )

    # Three test scenarios
    scenarios = [
        {
            "name": "Accidental collision damage",
            "document_type": "REPAIR_ESTIMATE",
            "document_text": """
            The vehicle sustained accidental collision damage.
            The repair estimate records damage to the front
            bumper and headlight caused by a road accident.
            """,
            "expected": "CONSISTENT",
        },
        {
            "name": "General wear and tear",
            "document_type": "VEHICLE_INSPECTION_REPORT",
            "document_text": """
            The vehicle has sustained damage due to gradual
            deterioration and general wear and tear.

            The inspection confirms that the damage did not
            result from an accident or collision.
            """,
            "expected": "INCONSISTENT",
        },
        {
            "name": "Flood damage without protection evidence",
            "document_type": "VEHICLE_INSPECTION_REPORT",
            "document_text": """
            The vehicle sustained damage due to flood water.
            The submitted inspection report does not contain
            any information confirming whether applicable
            natural disaster protection is included in the
            policy schedule.
            """,
            "expected": "NEEDS_REVIEW / INSUFFICIENT_EVIDENCE",
        },
    ]

    passed = 0

    print("\n========== POLICY SCENARIO TESTS ==========")

    for index, scenario in enumerate(scenarios, start=1):

        print("\n" + "=" * 70)
        print(f"SCENARIO {index}: {scenario['name']}")

        result = policy_service.validate_document(
            document_type=scenario["document_type"],
            document_text=scenario["document_text"],
            k=5,
        )

        actual = result.overall_status.value
        expected = scenario["expected"]

        print("EXPECTED:", expected)
        print("ACTUAL:", actual)
        print("RECOMMENDATION:", result.recommendation)

        for finding in result.findings:
            print("\nFINDING:", finding.finding)
            print("STATUS:", finding.status.value)
            print("EXPLANATION:", finding.explanation)

            for evidence in finding.evidence:
                print("EVIDENCE:", evidence.content)
                print("SOURCE:", evidence.source)
                print("PAGE:", evidence.page)

        if (
            actual == expected
            or (
                scenario["name"].startswith("Flood")
                and actual in (
                    "NEEDS_REVIEW",
                    "INSUFFICIENT_EVIDENCE",
                )
            )
        ):
            passed += 1
            print("\nSCENARIO RESULT: PASSED")
        else:
            print("\nSCENARIO RESULT: NEEDS INVESTIGATION")

    print("\n" + "=" * 70)
    print("TOTAL SCENARIOS:", len(scenarios))
    print("PASSED:", passed)
    print("NEEDS INVESTIGATION:", len(scenarios) - passed)

    print("\n========== TEST COMPLETED ==========")


if __name__ == "__main__":
    main()
