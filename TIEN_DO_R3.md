# NHẬT KÝ TIẾN ĐỘ CÔNG VIỆC — ROLE R3
**Phụ trách:** BM25, RRF, Fallback & Retrieval Pipeline  
**Module:** `src/task6_lexical_search.py`, `src/task7_reranking.py`, `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py`

---

## 📌 DANH SÁCH CÁC CÔNG VIỆC CẦN LÀM

- [x] **Công việc 1: Thuật toán RRF Reranking (`src/task7_reranking.py`)** ✅ *(Đã hoàn thành & Pass 100% Test Contract)*  
  *Gộp bảng xếp hạng Dense & BM25 theo công thức $RRF = \sum \frac{1}{60 + rank}$, rank từ 1, khử trùng lặp ID.*
- [x] **Công việc 2: Lexical Search bằng BM25 (`src/task6_lexical_search.py`)** ✅ *(Đã hoàn thành & Pass 100% Test Contract)*  
  *Xây dựng BM25 index trên corpus, tìm kiếm theo từ khóa, lọc score > 0, chuẩn hóa schema SearchResult.*
- [x] **Công việc 3: Vectorless / PageIndex Fallback (`src/task8_pageindex_vectorless.py`)** ✅ *(Đã hoàn thành & Pass 100% Test Contract)*  
  *Cài đặt fallback tìm kiếm không dùng vector, bọc try-except chống sập pipeline.*
- [x] **Công việc 4: Retrieval Pipeline Hợp nhất (`src/task9_retrieval_pipeline.py`)** ✅ *(Đã hoàn thành & Pass 100% Test Contract)*  
  *Điều phối Dense + BM25, chỉ gọi RRF 1 lần, so sánh ngưỡng với dense cosine score gốc để fallback.*
- [x] **Công việc 5: Thực nghiệm Hiệu chỉnh Ngưỡng (Calibration) & Báo cáo** ✅ *(Đã hoàn thành bảng số liệu & Báo cáo cá nhân)*  
  *Đo lường câu hỏi in-domain vs out-of-domain để chốt `SCORE_THRESHOLD = 0.40` tối ưu, hoàn thiện báo cáo mẫu.*

---

## 📝 NHẬT KÝ CHI TIẾT TỪNG BƯỚC

### ✅ Công việc 1: Hoàn thành Task 7 — RRF Reranking (`src/task7_reranking.py`)
- **Nội dung thực hiện:**
  - Viết hàm `rerank_rrf(ranked_lists, top_k=5, k=60)`.
  - Triển khai chính xác công thức Reciprocal Rank Fusion: với mỗi tài liệu $d$, tính tổng $\sum \frac{1}{k + rank_m(d)}$.
  - Đảm bảo biến `rank` được đánh số từ **1** (chuẩn theo yêu cầu của lab).
  - Tự động khử trùng lặp ID (deduplication) khi tài liệu xuất hiện ở cả danh sách Dense và BM25.
  - Định dạng chuẩn đầu ra `SearchResult` với nhãn `retrieval_method="hybrid"`.
- **Kết quả kiểm thử tự động:**
  - Lệnh: `pytest tests/test_contracts.py -k "test_rrf" -v`
  - Kết quả: **`test_rrf_uses_rank_deduplicates_and_marks_hybrid PASSED [100%]`**.
- **File / Commit / Bằng chứng:**
  - `src/task7_reranking.py`

---

### ✅ Công việc 2: Hoàn thành Task 6 — BM25 Lexical Search (`src/task6_lexical_search.py`)
- **Nội dung thực hiện:**
  - Viết hàm `build_bm25_index(corpus)` xây dựng chỉ mục `BM25Okapi` từ các chunk văn bản đã tokenize.
  - Viết hàm `lexical_search(query, top_k=10)` truy vấn từ khóa nhanh chóng theo điểm BM25.
  - Xử lý cơ chế cache index tự động để không phải build lại chỉ mục khi corpus không thay đổi.
  - Xử lý trường hợp biên (edge cases): lọc bỏ các tài liệu không chứa từ khóa (score $\le 0$) và xử lý tốt ngay cả khi tập kiểm thử có số lượng văn bản rất nhỏ.
  - Định dạng kết quả trả về đúng chuẩn `SearchResult` với nhãn `retrieval_method="bm25"`.
- **Kết quả kiểm thử tự động:**
  - Lệnh: `pytest tests/test_contracts.py -k "test_lexical" -v`
  - Kết quả: **`test_lexical_search_returns_bm25_contract PASSED [100%]`**.
- **File / Commit / Bằng chứng:**
  - `src/task6_lexical_search.py`

---

### ✅ Công việc 3: Hoàn thành Task 8 — Vectorless / PageIndex Fallback (`src/task8_pageindex_vectorless.py`)
- **Nội dung thực hiện:**
  - Viết hàm `upload_documents()` và `pageindex_search(query, top_k=5)`.
  - Hỗ trợ gọi PageIndex API khi có `PAGEINDEX_API_KEY` trong `.env`.
  - Xây dựng cơ chế fallback quét cấu trúc tài liệu cục bộ (`data/standardized/`) theo từ khóa và đề mục khi không có API key hoặc mất kết nối ngoài.
  - Bọc toàn bộ trong khối `try...except` để đảm bảo hệ thống không bao giờ crash nếu dịch vụ ngoài gặp sự cố.
  - Định dạng kết quả đầu ra đúng chuẩn `SearchResult` với nhãn `retrieval_method="pageindex"`, score sắp xếp giảm dần và đầy đủ metadata.
- **Kết quả kiểm thử tự động:**
  - Chữ ký hàm ổn định: `test_public_function_signatures_are_stable PASSED [100%]`.
  - Kiểm định hợp đồng: `validate_search_results` đạt 100% chuẩn `pageindex`.
- **File / Commit / Bằng chứng:**
  - `src/task8_pageindex_vectorless.py`

---

### ✅ Công việc 4: Hoàn thành Task 9 — Retrieval Pipeline Hợp nhất (`src/task9_retrieval_pipeline.py`)
- **Nội dung thực hiện:**
  - Viết hàm `retrieve(query, top_k=5, score_threshold=0.3, use_reranking=True)`.
  - Chạy đồng thời `semantic_search` (Dense) và `lexical_search` (BM25) để lấy danh sách ứng viên phong phú.
  - Trích xuất điểm tương đồng gốc tốt nhất `best_dense_score` từ kết quả Dense retrieval.
  - **Quy tắc Fallback chuẩn xác:** So sánh trực tiếp `best_dense_score < score_threshold` để quyết định kích hoạt fallback sang `pageindex_search` (tuyệt đối không so sánh với RRF score).
  - **Chống crash:** Bọc PageIndex fallback trong khối `try...except`, nếu dịch vụ ngoài gặp lỗi thì tự động rơi về kết quả Hybrid.
  - **Quy tắc RRF:** Khi dense score đạt ngưỡng tin cậy, gọi `rerank_rrf` đúng một lần duy nhất và không gọi fallback không cần thiết.
- **Kết quả kiểm thử tự động:**
  - `test_retrieve_uses_dense_score_for_fallback PASSED [100%]` ✅
  - `test_retrieve_fuses_once_when_dense_is_confident PASSED [100%]` ✅
  - `test_retrieve_survives_fallback_provider_error PASSED [100%]` ✅
- **File / Commit / Bằng chứng:**
  - `src/task9_retrieval_pipeline.py`

---

### ✅ Công việc 5: Thực nghiệm Hiệu chuẩn Ngưỡng & Báo cáo Nghiệm thu
- **Nội dung thực hiện:**
  - Xây dựng script thực nghiệm `scratch/calibrate_threshold.py` đo lường độ tương đồng cosine dense giữa 5 câu hỏi in-domain (Du lịch Việt Nam) và 4 câu hỏi out-of-domain (kỹ thuật, toán học, y tế).
  - Kết quả đo đạc: Điểm in-domain đạt $0.69 - 0.81$ (trung bình $0.75$), điểm out-of-domain chỉ đạt $0.08 - 0.22$ (trung bình $0.15$).
  - Thiết lập giá trị tối ưu: Chốt **`SCORE_THRESHOLD = 0.40`** và ghi nhận vào `.env`.
  - Soạn sẵn toàn bộ nội dung Báo cáo đóng góp cá nhân chuẩn chỉnh theo đúng template 1 trang tại: `reports/R3-BM25-RRF-Retrieval-Pipeline.md` (bao gồm đầy đủ bảng phân công, 2 quyết định kỹ thuật sâu sắc, kết quả test và hướng hạn chế/cải tiến).
- **File / Bằng chứng:**
  - `scratch/calibrate_threshold.py`
  - `.env`
  - `reports/R3-BM25-RRF-Retrieval-Pipeline.md`
