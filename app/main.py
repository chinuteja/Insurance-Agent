from fastapi import FastAPI

app = FastAPI(
    title="Insurance AI Agent Platform",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "insurance-ai-agent-platform"
    }