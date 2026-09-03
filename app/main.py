from fastapi import FastAPI

from app.routers.customer_router import router as customer_router
from app.routers.policy_router import router as policy_router
from app.routers.claim_router import router as claim_router
from app.routers.document_router import router as document_router


app = FastAPI(
    title="Insurance AI Agent Platform",
    version="0.1.0",
    description="Agentic AI platform for insurance claim processing"
)


app.include_router(customer_router)
app.include_router(policy_router)
app.include_router(claim_router)
app.include_router(document_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Insurance AI Agent Platform",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "insurance-ai-agent-platform"
    }