from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.auth.router import router as auth_router, users_router
from app.chat.router import router as chat_router
from app.documents.router import router as documents_router
from app.retrieval.router import router as retrieval_router


app = FastAPI(
    title="RAG Monolith API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(retrieval_router)
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/health")
def health_check():
    return {"status": "ok"}
