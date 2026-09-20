# Báo cáo cá nhân — Lab 08 RAG Pipeline

## Thông tin

- **Họ và tên:** Phạm Đức Anh
- **Mã học viên:** 2A202602994
- **Nhóm:** Top1Server
- **Vai trò:** R2 — Chunking, Embedding, Vector Indexing và Dense Retrieval
- **Repository/branch:** `tungne1311/K4-L3A-RAG-Pipeline-Top1Server` — `feature/dense-retrieval`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 4 — Load documents | Đọc 13 file Markdown do R1 chuẩn hoá; tạo ID ổn định và trích xuất title, source, doc_type, URL. | `src/task4_chunking_indexing.py` — `75b6ffb` | Done |
| Task 4 — Chunking | Dùng RecursiveCharacterTextSplitter với chunk size 500, overlap 50; giữ metadata và bổ sung chunk_index. | `src/task4_chunking_indexing.py` — `75b6ffb` | Done |
| Task 4 — Embedding/indexing | Dùng BAAI/bge-m3, chuẩn hoá vector; cache model; upsert theo batch vào ChromaDB cosine với ID ổn định. | `src/task4_chunking_indexing.py` — `75b6ffb` | Done |
| Task 5 — Dense retrieval | Embed query bằng cùng model Task 4, truy vấn ChromaDB, đổi cosine distance thành similarity và sắp xếp giảm dần. | `src/task5_semantic_search.py` — `339fcc6` | Done |
| Contract test | Cài dependencies và chạy bộ contract test; các test thuộc Task 4–5 vượt qua. | `python -m pytest tests/test_contracts.py -q` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Recursive chunking với `CHUNK_SIZE=500`, `CHUNK_OVERLAP=50`.
   - **Lý do/evidence:** Corpus gồm văn bản pháp lý dài và bài tin Markdown; tách ưu tiên theo đoạn, dòng, câu và từ giúp hạn chế cắt vỡ ngữ nghĩa. Overlap giữ ngữ cảnh ở biên chunk.
   - **Trade-off:** Overlap tăng số vector và chi phí lưu trữ; cấu hình cần được đánh giá thêm bằng golden set.

2. **Quyết định:** Dùng `BAAI/bge-m3` cho cả document và query, chuẩn hoá embedding và dùng ChromaDB cosine.
   - **Lý do/evidence:** BGE-M3 hỗ trợ dữ liệu đa ngôn ngữ, phù hợp corpus tiếng Việt; dùng chung model giữ query và document trong cùng không gian vector.
   - **Trade-off:** Model lớn nên lần tải/chạy đầu chậm và cần nhiều tài nguyên.

## Kiểm thử và kết quả

- **Test đã dùng:** `python -m pytest tests/test_contracts.py -q`.
- **Kết quả:** `9 passed, 6 failed`. Sáu failure đều là `NotImplementedError` ở Task 6, 7, 9 và 10 của R3/R4; không có failure tại Task 4 hoặc Task 5 của R2.
- **Lỗi đã phát hiện:** Môi trường ban đầu thiếu `pytest`, `langchain-text-splitters` và `sentence-transformers`.
- **Cách xử lý:** Cài dependencies bằng `python -m pip install -e ".[dev]"`.
- **Smoke test corpus thật:** Chưa hoàn tất do lần đầu tải BGE-M3 mất nhiều thời gian; code được chuyển giao sớm để R3/R4 tích hợp song song.

## Điều còn hạn chế

- Chưa ghi nhận thời gian indexing, tổng số chunk, dung lượng ChromaDB và chất lượng top-k vì model chưa tải xong.
- Chưa so sánh thực nghiệm nhiều cấu hình chunk hoặc model embedding khác.
- Nếu có thêm thời gian, tôi sẽ hoàn tất smoke test end-to-end và thử các query về phí tham quan, quy định bảo tồn và lịch trình Hội An — Đà Nẵng.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 20/09/2026
- **Tên thành viên:** Phạm Đức Anh
