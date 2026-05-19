from fastapi import FastAPI
from app.documents.router import router as documents_router


app = FastAPI(
    title="RAG Monolith API",
    version="1.0.0"
)


app.include_router(documents_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}