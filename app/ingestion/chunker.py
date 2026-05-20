from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentChunker:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def split(self, documents):
        return self.splitter.split_documents(documents)