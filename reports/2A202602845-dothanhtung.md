# Individual contribution report

## Thông tin

- Họ và tên: Đỗ Thanh Tùng
- Mã học viên: 2A202602845
- Nhóm: <ĐIỀN tên/số nhóm>
- Repository/branch: K4-L3A-RAG-Pipeline-Top1Server / main
- Vai trò: **R1 — Data & Standardization**

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 1 — thu thập văn bản pháp quy | Chốt nguồn (kho văn bản Trung tâm QLBT Di sản Văn hóa Hội An), viết `download_documents()` tải resume qua HTTP Range + verify toàn vẹn PDF; thu 5 văn bản của UBND Quảng Nam / UBND Hội An | `src/task1_collect_legal_docs.py`, `data/landing/legal/*.pdf` — commit `<ĐIỀN>` | Done |
| Task 2 — crawl bài viết | Chọn 8 URL từ danang.gov.vn, baodanang.vn, danangfantasticity.com, baovanhoa.vn; viết `crawl_article()` hai nhánh Crawl4AI → requests/BeautifulSoup, lọc `nav/header/footer/aside/script` và dò khối nội dung chính | `src/task2_crawl_news.py`, `data/landing/news/article_0*.json` — commit `<ĐIỀN>` | Done |
| Task 3 — chuẩn hoá Markdown | Convert PDF bằng MarkItDown, JSON → Markdown; chèn header metadata (title/source/doc_type/URL/issuer) để Task 10 dựng citation; chuẩn hoá khoảng trắng | `src/task3_convert_markdown.py`, `data/standardized/{legal,news}/*.md` — commit `<ĐIỀN>` | Done |
| Danh sách nguồn cho citation | Viết `write_source_manifest()` sinh bảng file ↔ tiêu đề ↔ cơ quan ban hành ↔ URL để R4 đối chiếu citation | `data/SOURCES.md` — commit `<ĐIỀN>` | Done |

**Kết quả corpus:** 5 văn bản pháp quy (PDF) + 8 bài viết (JSON) → 13 file Markdown, tổng ~213.700 ký tự.

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Tải tài liệu theo cơ chế resume (HTTP `Range`) kèm vòng lặp xác minh toàn vẹn, thay vì `requests.get()` một lần.
   **Lý do/evidence:** Server `hoianheritage.net` đóng kết nối sớm. Tải một lần bằng `curl` cho ra file 196.608 byte thiếu marker `%%EOF`, trong khi file đủ là 1.686.198 byte; cùng một URL còn trả kích thước khác nhau giữa các lần (540.672 vs 286.720 byte). 4/5 file thử ban đầu đều bị cắt. Sau khi thêm resume + kiểm tra `%PDF` ở đầu và `%%EOF` ở cuối, tỉ lệ tải đủ là 5/5.
   **Trade-off:** Mỗi file có thể phải gọi mạng nhiều lần nên chậm hơn; đổi lại không có file hỏng lọt vào corpus. Tôi cũng phải thêm guard cho trường hợp server trả 206 nhưng bỏ qua offset khiến file phình mãi không đủ (phát hiện qua delta lặp lại → xoá và tải lại từ đầu).

2. **Quyết định:** `crawl_article()` thử Crawl4AI trước, thất bại thì fallback sang `requests` + BeautifulSoup rồi tự chuyển sang Markdown.
   **Lý do/evidence:** Tôi kiểm tra trước bằng `curl` thì cả 8 trang đều render server-side, HTML thuần đã đủ nội dung — không cần trình duyệt. Thực tế khi chạy, Crawl4AI không khởi tạo được (chưa `playwright install chromium`) và cả 8 bài đều đi nhánh fallback, vẫn thu đủ 567–7.813 ký tự mỗi bài.
   **Trade-off:** Hai nhánh code nhiều hơn một, và nhánh fallback sẽ không lấy được nội dung nếu sau này nhóm thêm nguồn render bằng JavaScript. Đổi lại corpus vẫn hoàn chỉnh trên máy chưa cài Chromium (~400 MB).

## Kiểm thử và kết quả

- Test đã dùng: `pytest tests/test_acceptance.py -q` → **3 passed** cho đúng ba test thuộc phần dữ liệu (`test_corpus_has_required_legal_documents`, `test_corpus_has_required_news_with_metadata`, `test_standardized_output_covers_both_source_types`). Hai test còn lại (`golden_dataset`, `RESULT.md`) thuộc phần evaluation, không thuộc phạm vi R1.
- Kiểm tra chạy lại: chạy Task 1→2→3 lần hai, số file trong `data/` giữ nguyên 27 → không sinh file trùng.
- Kiểm tra chất lượng: script đếm lỗi font (ký tự thay thế), tách chữ giữa từ và khoảng trắng thừa trên cả 13 file → cả ba chỉ số về **0**.

**Lỗi đã phát hiện và cách xử lý**

| Lỗi | Biểu hiện | Xử lý |
|---|---|---|
| File tải bị cắt | PDF thiếu `%%EOF`, kích thước khác nhau mỗi lần tải | Resume + verify toàn vẹn, retry tối đa 6 lần |
| `UnicodeEncodeError` khi log | Console Windows cp1252 không in được tiếng Việt; file **đã ghi thành công** nhưng log báo "Failed" gây hiểu nhầm | `sys.stdout.reconfigure(encoding="utf-8")` ở đầu Task 2 và Task 3 |
| PDF scan không có text layer | `351/QĐ-UBND` (Kế hoạch quản lý di sản 2020-2025) trích được **0 ký tự** | Thay bằng Quy chế quản lý, bảo vệ và phát huy giá trị di tích tỉnh Quảng Nam (45.036 ký tự); Task 3 thêm nhánh bỏ qua file <200 ký tự kèm cảnh báo thay vì ghi file rỗng |
| Khoảng trắng thừa trong PDF | Văn bản căn đều lề khiến pdfminer chèn 2+ space giữa các từ (1.328 chỗ trong một file) | Thêm `_MULTI_SPACES` vào `_normalise()`; sau chuẩn hoá còn 0, tiết kiệm ngân sách `chunk_size=500` của Task 4 |

## Điều còn hạn chế

- Corpus phải loại Quyết định 351/QĐ-UBND — một văn bản quan trọng về kế hoạch quản lý di sản — chỉ vì bản PDF công bố là bản scan và pipeline của tôi chưa có OCR. Ngoài ra `article_03.md` chỉ 773 ký tự, mỏng hơn hẳn các bài còn lại nên nhiều khả năng sẽ đóng góp ít cho retrieval.
- Nếu có thêm thời gian, việc đầu tiên tôi làm là thêm bước OCR (ocrmypdf/Tesseract với gói ngôn ngữ `vie`) cho các PDF trích được dưới ngưỡng, để lấy lại những văn bản dạng scan thay vì loại bỏ chúng.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: <ĐIỀN>
- Tên thành viên: Đỗ Thanh Tùng
