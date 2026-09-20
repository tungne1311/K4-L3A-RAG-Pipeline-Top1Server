"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 4 & Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu, địa danh và tên riêng. Output phải tuân thủ SearchResult và sắp xếp score giảm dần.
"""

from typing import Any
import numpy as np
from rank_bm25 import BM25Okapi


CORPUS: list[dict] = []
_BM25_INDEX: BM25Okapi | None = None
_CACHED_CORPUS_ID: int | None = None


def build_bm25_index(corpus: list[dict]) -> BM25Okapi | None:
    """
    Tạo BM25 index từ corpus chunks (cùng corpus với Task 4 và Task 5).
    
    Args:
        corpus: Danh sách Document chunks có trường "content".
        
    Returns:
        Đối tượng BM25Okapi đã được lập chỉ mục.
    """
    if not corpus:
        return None
    tokenized_corpus = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized_corpus)


def _ensure_corpus_and_index():
    """Tự động nạp corpus từ Task 4 nếu CORPUS hiện tại đang rỗng và cập nhật index cache."""
    global CORPUS, _BM25_INDEX, _CACHED_CORPUS_ID

    if not CORPUS:
        try:
            from .task4_chunking_indexing import chunk_documents, load_documents
            documents = load_documents()
            CORPUS = chunk_documents(documents)
        except Exception:
            CORPUS = []

    current_corpus_id = id(CORPUS)
    if _BM25_INDEX is None or _CACHED_CORPUS_ID != current_corpus_id:
        _BM25_INDEX = build_bm25_index(CORPUS)
        _CACHED_CORPUS_ID = current_corpus_id


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khóa bằng thuật toán BM25 và trả về danh sách SearchResult.
    
    Args:
        query: Chuỗi truy vấn tìm kiếm từ người dùng.
        top_k: Số lượng kết quả tối đa cần trả về (mặc định 10).
        
    Returns:
        Danh sách SearchResult được sắp xếp theo BM25 score giảm dần.
        Mỗi phần tử gồm: id, content, score, metadata, retrieval_method="bm25".
    """
    _ensure_corpus_and_index()

    if not CORPUS or _BM25_INDEX is None:
        return []

    tokenized_query = query.lower().split()
    if not tokenized_query:
        return []

    # Tính điểm BM25 cho câu truy vấn
    raw_scores = _BM25_INDEX.get_scores(tokenized_query)
    scores: list[float] = []

    # Xử lý trường hợp corpus nhỏ (như unit test) nơi IDF của BM25Okapi có thể bằng 0
    query_terms = set(tokenized_query)
    for idx, raw_score in enumerate(raw_scores):
        if raw_score > 0.0:
            scores.append(float(raw_score))
        else:
            doc_tokens = CORPUS[idx]["content"].lower().split()
            matched_count = sum(1 for term in query_terms if term in doc_tokens)
            if matched_count > 0:
                # Đảm bảo tài liệu có chứa từ khóa có score dương
                scores.append(float(matched_count))
            else:
                scores.append(0.0)

    ranked_indices = np.argsort(scores)[::-1]

    results: list[dict] = []
    for index in ranked_indices:
        score = scores[index]
        # Bỏ qua các tài liệu không chứa bất kỳ từ khóa nào
        if score <= 0.0:
            continue

        item = CORPUS[index]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": score,
            "metadata": item.get("metadata", {}),
            "retrieval_method": "bm25",
        })

        if len(results) >= top_k:
            break

    return results


if __name__ == "__main__":
    sample_corpus = [
        {"id": "c-1", "content": "Vé tham quan Phố cổ Hội An có giá 80.000 VNĐ.", "metadata": {"source": "hoi_an.md", "chunk_index": 0}},
        {"id": "c-2", "content": "Bà Nà Hills nằm ở độ cao 1487m so với mực nước biển.", "metadata": {"source": "ba_na.md", "chunk_index": 1}},
        {"id": "c-3", "content": "Thời gian lý tưởng du lịch Hà Nội là mùa thu.", "metadata": {"source": "ha_noi.md", "chunk_index": 2}},
    ]
    CORPUS = sample_corpus
    print("Ket qua lexical search cho 'Hoi An':")
    for r in lexical_search("Hoi An", top_k=2):
        print(f"[{r['retrieval_method']}] ID: {r['id']}, Score: {r['score']:.4f}, Content: {r['content']}")
