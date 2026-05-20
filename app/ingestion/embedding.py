from langchain_huggingface import HuggingFaceEndpointEmbeddings
from app.config import settings

_embeddings = None


def get_embeddings():
    global _embeddings

    if _embeddings is None:
        _embeddings = HuggingFaceEndpointEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2",
            huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN
        )

    return _embeddings


def embed_texts(texts: list[str]) -> list[list[float]]:
    embeddings = get_embeddings()
    return embeddings.embed_documents(texts)