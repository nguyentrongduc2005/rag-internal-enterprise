from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from app.config import settings


def get_qwen_chat_model(streaming: bool = False) -> ChatHuggingFace:
    endpoint = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-7B-Instruct",
        task="text-generation",
        temperature=0.1,
        huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN,
        max_new_tokens=512,
        streaming=streaming,
    )
    return ChatHuggingFace(llm=endpoint, streaming=streaming)
