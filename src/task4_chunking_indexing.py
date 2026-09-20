"""Task 4 — Chunking, embedding và indexing."""

from functools import lru_cache
from pathlib import Path
import re

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
COLLECTION_NAME = "rag_documents"
BATCH_SIZE = 100


@lru_cache(maxsize=1)
def _embedding_model():
    """Nạp model một lần để indexing và query dùng chung model."""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    provider = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers").lower()
    if provider != "sentence_transformers":
        raise ValueError(f"Chỉ hỗ trợ sentence_transformers, config yêu cầu: {provider}")
        
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Tạo dense embeddings theo đúng thứ tự input."""
    if not texts:
        return []
    vectors = _embedding_model().encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    )
    return vectors.tolist()


def get_collection():
    """Mở persistent Chroma collection dùng cosine distance."""
    import chromadb
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


def _metadata_from_markdown(path: Path, content: str) -> dict:
    """Đọc metadata do R1 ghi trong Markdown, có fallback theo đường dẫn."""
    title_match = re.search(r"^#\s+(.+)$", content, flags=re.MULTILINE)
    source_match = re.search(r"\*\*Source:\*\*\s*(.+)", content)
    type_match = re.search(r"\*\*Doc type:\*\*\s*(.+)", content)
    url_match = re.search(r"\*\*URL:\*\*\s*(\S+)", content)
    inferred_type = "legal" if "legal" in path.parts else "news"
    return {
        "source": source_match.group(1).strip() if source_match else path.name,
        "title": title_match.group(1).strip() if title_match else path.stem,
        "doc_type": type_match.group(1).strip() if type_match else inferred_type,
        "url": url_match.group(1).strip() if url_match else None,
    }


def load_documents() -> list[dict]:
    """Đọc mọi Markdown chuẩn hoá thành Document theo contract."""
    if not STANDARDIZED_DIR.exists():
        return []
    documents = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if path.name == ".gitkeep":
            continue
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        documents.append({
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": content,
            "metadata": _metadata_from_markdown(path, content),
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có ID ổn định và giữ provenance."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for document in documents:
        for index, text in enumerate(splitter.split_text(document["content"])):
            if text.strip():
                chunks.append({
                    "id": f"{document['id']}::chunk-{index}",
                    "content": text,
                    "metadata": {**document["metadata"], "chunk_index": index},
                })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    if not chunks:
        return []
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    if len(vectors) != len(chunks):
        raise ValueError("Embedding provider trả về sai số lượng vectors")
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def _chroma_metadata(metadata: dict) -> dict:
    """Loại None vì Chroma chỉ nhận metadata scalar."""
    return {key: value for key, value in metadata.items() if value is not None}


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks theo batch; chạy lại không tạo dữ liệu trùng."""
    if not chunks:
        return
    collection = get_collection()
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            documents=[chunk["content"] for chunk in batch],
            embeddings=[chunk["embedding"] for chunk in batch],
            metadatas=[_chroma_metadata(chunk["metadata"]) for chunk in batch],
        )


def run_pipeline() -> None:
    """Chạy load → chunk → embed → index."""
    documents = load_documents()
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks from {len(documents)} documents")


if __name__ == "__main__":
    run_pipeline()
