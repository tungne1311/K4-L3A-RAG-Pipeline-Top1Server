"""
Task 9 — Retrieval pipeline hoàn chỉnh.

Luồng xử lý:
    1. Chạy semantic_search (dense) và lexical_search (sparse).
    2. Lấy best cosine score gốc từ dense results.
    3. Nếu score dưới threshold, kích hoạt PageIndex vectorless fallback.
    4. Nếu fallback thành công, trả kết quả pageindex.
    5. Nếu score đạt ngưỡng (hoặc fallback lỗi/không có kết quả), fuse hai danh sách
       bằng RRF đúng một lần và trả hybrid results, không bao giờ để crash.

Lưu ý bất biến:
    - Tuyệt đối so sánh threshold với cosine score gốc của dense search,
      không so sánh với RRF score vì hai thang đo hoàn toàn khác nhau.
    - RRF chỉ được gọi tối đa một lần trong pipeline.
"""

import os
from dotenv import load_dotenv

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


load_dotenv()

_env_thresh = os.getenv("SCORE_THRESHOLD")
try:
    SCORE_THRESHOLD = float(_env_thresh) if _env_thresh else 0.3
except ValueError:
    SCORE_THRESHOLD = 0.3

DEFAULT_TOP_K = 5


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """
    Điều phối tìm kiếm hỗn hợp (Hybrid Search) kết hợp cơ chế Fallback an toàn.
    
    Args:
        query: Câu truy vấn của người dùng.
        top_k: Số lượng kết quả cần lấy (mặc định 5).
        score_threshold: Ngưỡng cosine score tối thiểu của dense search để không kích hoạt fallback.
        use_reranking: Boolean xác định có dùng RRF để gộp dense và bm25 hay không.
        
    Returns:
        Danh sách SearchResult (thuộc method 'hybrid' hoặc 'pageindex').
    """
    # 1. Chạy song song Dense Search và BM25 Lexical Search (lấy top_k * 2 để có ứng viên phong phú)
    dense_candidates = semantic_search(query, top_k=top_k * 2)
    sparse_candidates = lexical_search(query, top_k=top_k * 2)

    # 2. Lấy điểm tương đồng cosine tốt nhất từ kết quả Dense (top-1 dense score)
    best_dense_score = float(dense_candidates[0]["score"]) if dense_candidates else 0.0

    # 3. Kiểm tra điều kiện Fallback:
    # Nếu điểm dense thấp hơn ngưỡng (câu hỏi ngoài domain hoặc không tự tin)
    if best_dense_score < score_threshold:
        try:
            fallback_results = pageindex_search(query, top_k=top_k)
            if fallback_results:
                return fallback_results[:top_k]
        except Exception:
            # Nếu nhà cung cấp PageIndex bị lỗi/mất mạng, không làm sập chương trình mà tiếp tục luồng hybrid
            pass

    # 4. Khi dense score tự tin (hoặc fallback lỗi/không có dữ liệu):
    # Tiến hành hợp nhất Dense và BM25 bằng RRF đúng một lần duy nhất
    if use_reranking:
        hybrid_results = rerank_rrf([dense_candidates, sparse_candidates], top_k=top_k)
    else:
        hybrid_results = dense_candidates[:top_k]

    return hybrid_results[:top_k]


if __name__ == "__main__":
    print("Testing retrieve pipeline:")
    results = retrieve("Quy định du lịch", top_k=3)
    for r in results:
        print(f"[{r.get('retrieval_method')}] Score: {r.get('score')} - ID: {r.get('id')}")
