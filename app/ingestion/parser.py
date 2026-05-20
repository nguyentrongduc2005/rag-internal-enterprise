import re
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PDFPlumberLoader,
    TextLoader,
    Docx2txtLoader,
    CSVLoader
)


class DocumentParser:
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        # 1. Loại bỏ các ký tự NUL
        text = text.replace('\x00', '')
        # 2. Xóa các chuỗi mã unicode kỳ lạ dạng /uniXXXX... thường xuất hiện khi đọc PDF lỗi font
        text = re.sub(r'(/uni[0-9a-fA-F]{8}|/uni[0-9a-fA-F]{4})', '', text)
        # 3. Xóa các khoảng trắng thừa (giữ lại khoảng trắng đơn)
        text = re.sub(r' +', ' ', text)
        # 4. Gom các dòng trống liên tiếp (chỉ giữ tối đa 2 dấu xuống dòng để không mất format đoạn văn)
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 5. Loại bỏ khoảng trắng ở đầu và cuối
        return text.strip()

    def parse(self, file_path: str) -> list[Document]:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            loader = PDFPlumberLoader(str(path))
        elif suffix in [".txt", ".md"]:
            loader = TextLoader(str(path), encoding="utf-8")
        elif suffix == ".docx":
            loader = Docx2txtLoader(str(path))
        elif suffix == ".csv":
            loader = CSVLoader(str(path))
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        # Load dữ liệu
        docs = loader.load()

        # Clean text data
        for doc in docs:
            doc.page_content = self.clean_text(doc.page_content)

        return docs