"""
Task 7 — Reciprocal Rank Fusion (RRF).

RRF gộp nhiều bảng xếp hạng (Dense + BM25) mà không cộng trực tiếp cosine score với BM25 score.
Công thức: RRF(d) = sum(1 / (k + rank)), rank bắt đầu từ 1.
Lưu ý: RRF score chỉ phản ánh thứ hạng, không dùng để quyết định fallback.
"""


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """
    Fuse nhiều ranked lists và trả hybrid SearchResult theo chuẩn contract.
    
    Args:
        ranked_lists: Danh sách các danh sách kết quả tìm kiếm (VD: [dense_results, bm25_results]).
        top_k: Số lượng kết quả tối đa cần trả về.
        k: Hằng số làm trơn (mặc định là 60).
        
    Returns:
        Danh sách SearchResult đã được rerank theo điểm RRF giảm dần, khử trùng lặp id,
        và có retrieval_method = "hybrid".
    """
    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, start=1):
            item_id = item["id"]
            reciprocal_rank_score = 1.0 / (k + rank)
            scores[item_id] = scores.get(item_id, 0.0) + reciprocal_rank_score
            
            # Lưu lại item đầu tiên gặp để giữ nguyên content và metadata
            if item_id not in items:
                items[item_id] = item

    # Sắp xếp các id theo điểm RRF giảm dần
    ranked_ids = sorted(scores.keys(), key=lambda doc_id: scores[doc_id], reverse=True)

    # Đóng gói kết quả đầu ra theo đúng SearchResult schema
    results: list[dict] = []
    for item_id in ranked_ids[:top_k]:
        result = items[item_id].copy()
        result["score"] = scores[item_id]
        result["retrieval_method"] = "hybrid"
        results.append(result)

    return results


if __name__ == "__main__":
    # Test nhanh logic RRF
    sample_dense = [
        {"id": "doc1", "content": "A", "score": 0.9, "metadata": {}, "retrieval_method": "dense"},
        {"id": "doc2", "content": "B", "score": 0.8, "metadata": {}, "retrieval_method": "dense"},
    ]
    sample_bm25 = [
        {"id": "doc2", "content": "B", "score": 5.0, "metadata": {}, "retrieval_method": "bm25"},
        {"id": "doc3", "content": "C", "score": 4.0, "metadata": {}, "retrieval_method": "bm25"},
    ]
    fused = rerank_rrf([sample_dense, sample_bm25], top_k=2)
    print("Ket qua RRF test:")
    for r in fused:
        print(f"ID: {r['id']}, Score: {r['score']:.5f}, Method: {r['retrieval_method']}")
