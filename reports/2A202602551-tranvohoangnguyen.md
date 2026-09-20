# Individual contribution report

## Thông tin

- Họ và tên: Trần Võ Hoàng Nguyên
- Mã học viên: 2A202602551
- Nhóm: Top 1 Server (Chủ đề: Trợ lý du lịch Đà Nẵng – Hội An)
- Repository/branch: `feature/hybrid-fallback`

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 6: Lexical search (BM25) | Viết hàm xây dựng chỉ mục `build_bm25_index` và hàm tìm kiếm `lexical_search`, thêm cơ chế cache index để tránh tính toán lại, lọc bỏ các văn bản có điểm số $\le 0$. | `src/task6_lexical_search.py` | Done |
| Task 7: Reranking (RRF) | Cài đặt thuật toán Reciprocal Rank Fusion gộp hai bảng xếp hạng Dense và BM25 theo công thức chuẩn $1/(60+rank)$, khử trùng lặp theo ID và gán nhãn `hybrid`. | `src/task7_reranking.py` | Done |
| Task 8: Vectorless Fallback | Viết hàm `pageindex_search` dự phòng; bọc khối `try...except` và xây dựng logic quét văn bản cục bộ để hệ thống không bị crash khi mất mạng hoặc không có API key. | `src/task8_pageindex_vectorless.py` | Done |
| Task 9: Retrieval Pipeline | Hợp nhất toàn bộ luồng tìm kiếm trong hàm `retrieve`; dùng điểm Cosine gốc của Dense search để so sánh với ngưỡng fallback; đảm bảo RRF chỉ chạy duy nhất 1 lần. | `src/task9_retrieval_pipeline.py` | Done |
| Calibration Threshold | Viết script chạy thử các câu hỏi du lịch thực tế (in-domain) và câu hỏi ngoài lề (out-of-domain) để tìm ra ngưỡng `SCORE_THRESHOLD = 0.40` đưa vào cấu hình `.env`. | `scratch/calibrate_threshold.py`, `.env` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng thuật toán RRF (Reciprocal Rank Fusion) để gộp thứ hạng thay vì cộng gộp điểm số trực tiếp (score fusion) giữa Dense và BM25.  
   **Lý do/evidence:** Điểm của Dense Search là Cosine Similarity nằm trong đoạn $[0, 1]$, trong khi điểm BM25 là điểm số không bị chặn trên (thường dao động từ vài điểm đến vài chục điểm). Nếu cộng trực tiếp, BM25 sẽ lấn át hoàn toàn Dense. Nếu chuẩn hóa min-max thì rất nhạy cảm với các tài liệu ngoại lai (outliers). RRF chỉ dùng thứ hạng ($rank$) nên giải quyết triệt để sự khập khiễng về thang điểm này và giúp code pass toàn bộ test contract.  
   **Trade-off:** RRF bỏ qua mức độ cách biệt điểm số thực tế giữa các tài liệu liền kề (ví dụ: tài liệu top 1 vượt trội hơn hẳn top 2 thì điểm số qua RRF cũng chỉ hơn một lượng nhỏ theo công thức nghịch đảo).

2. **Quyết định:** Dùng Cosine score gốc của Dense Retrieval để quyết định Fallback thay vì dùng điểm số RRF sau khi fuse.  
   **Lý do/evidence:** Điểm RRF chỉ là phép tính thứ hạng tương đối trên tập kết quả trả về. Dù người dùng hỏi một câu hoàn toàn lạc đề (out-of-domain), hệ thống vẫn luôn tìm ra các tài liệu xếp hạng 1, 2, 3 và sinh ra điểm RRF khoảng $0.016$, khiến ta không thể đặt ngưỡng chặn. Ngược lại, Cosine score phản ánh khoảng cách ngữ nghĩa thực tế: câu hỏi đúng chủ đề đạt điểm từ $0.69 - 0.81$, còn câu hỏi lạc đề chỉ đạt $0.08 - 0.22$. Nhờ đó, việc so sánh với ngưỡng $0.40$ hoạt động rất chính xác.  
   **Trade-off:** Phải phụ thuộc vào chất lượng của mô hình embedding ban đầu (`BAAI/bge-m3`) và cần chạy thực nghiệm đo đạc trước để chọn ngưỡng phù hợp cho từng bộ dữ liệu.

---

## Kiểm thử và kết quả

- **Test hoặc query tôi đã dùng:**  
  Chạy toàn bộ các bài test hợp đồng của Task 6 đến Task 9 bằng lệnh:
  ```powershell
  pytest tests/test_contracts.py -k "test_lexical or test_rrf or test_retrieve" -v
  ```
- **Kết quả trước/sau nếu có:**  
  100% các bài test đều đạt trạng thái PASSED:
  - `test_lexical_search_returns_bm25_contract PASSED`
  - `test_rrf_uses_rank_deduplicates_and_marks_hybrid PASSED`
  - `test_retrieve_uses_dense_score_for_fallback PASSED`
  - `test_retrieve_fuses_once_when_dense_is_confident PASSED`
  - `test_retrieve_survives_fallback_provider_error PASSED`
- **Lỗi đã phát hiện và cách xử lý:**  
  Khi chạy test cho BM25 lần đầu, hàm bị trả về danh sách rỗng dẫn đến `IndexError`. Sau khi debug, tôi phát hiện trong bài test của lab chỉ có 2 tài liệu mẫu, khiến công thức IDF trong thư viện `rank_bm25` bị tính ra bằng 0 ($IDF = \ln(1) = 0$). Tôi đã khắc phục bằng cách bổ sung thêm bước kiểm tra tần suất từ khóa thực tế: nếu điểm BM25 bằng 0 nhưng tài liệu có chứa từ khóa truy vấn thì vẫn gán điểm dương để giữ lại tài liệu phù hợp.

---

## Điều còn hạn chế

- **Một hạn chế cụ thể của phần tôi làm:**  
  Module BM25 hiện tại đang tokenize bằng cách cắt chuỗi theo khoảng trắng (`split()`), do đó chưa nhận diện tốt các từ ghép trong tiếng Việt (ví dụ: *"Bà Nà Hills"*, *"Ngũ Hành Sơn"*, *"phố cổ"* bị tách thành các từ đơn lẻ).
- **Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:**  
  Tích hợp thêm một thư viện tách từ tiếng Việt chuyên biệt (như `underthesea` hoặc `pyvi`) vào trước bước đánh chỉ mục BM25 để nâng cao độ chính xác khi tìm kiếm các địa danh và món ăn đặc sản.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 20/09/2026
- Tên thành viên: Trần Võ Hoàng Nguyên
