class PromptBuilder:
    def build(self, question: str, chunks: list[dict]) -> str:
        context_text = "\n\n".join(
            [
                f"[SOURCE {i + 1}]\n"
                f"File: {chunk.get('filename')}\n"
                f"Page: {chunk.get('page_number')}\n"
                f"Content:\n{chunk.get('content')}"
                for i, chunk in enumerate(chunks)
            ]
        )

        return f"""
Bạn là trợ lý AI trả lời câu hỏi dựa trên tài liệu được cung cấp.

Quy tắc:
- Chỉ trả lời dựa trên CONTEXT.
- Nếu CONTEXT không có thông tin, hãy nói: "Tôi không tìm thấy thông tin trong tài liệu."
- Trả lời ngắn gọn, rõ ràng.
- Có thể trích nguồn theo dạng [SOURCE 1], [SOURCE 2].

CONTEXT:
{context_text}

QUESTION:
{question}

ANSWER:
"""