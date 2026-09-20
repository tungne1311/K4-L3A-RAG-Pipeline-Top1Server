"""Task 5 — Dense semantic search trên ChromaDB."""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần, không quá top_k."""
    if not query or top_k <= 0:
        return []

    vectors = embed_texts([query])
    if not vectors:
        return []

    response = get_collection().query(
        query_embeddings=[vectors[0]],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    ids = (response.get("ids") or [[]])[0] or []
    documents = (response.get("documents") or [[]])[0] or []
    metadatas = (response.get("metadatas") or [[]])[0] or []
    distances = (response.get("distances") or [[]])[0] or []

    results = []
    for item_id, content, metadata, distance in zip(
        ids, documents, metadatas, distances
    ):
        similarity = max(0.0, min(1.0, 1.0 - float(distance)))
        results.append({
            "id": item_id,
            "content": content,
            "score": similarity,
            "metadata": metadata or {},
            "retrieval_method": "dense",
        })
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    for result in semantic_search("Vé tham quan phố cổ Hội An bao nhiêu?", top_k=3):
        print(result)
