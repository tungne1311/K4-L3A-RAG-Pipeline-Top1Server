# Individual contribution report

Mỗi thành viên copy template này thành:

```text
reports/<student-id>-<short-name>.md
```

Giới hạn khuyến nghị: 1 trang, không chép lại README hoặc mô tả lý thuyết chung. Báo cáo không phải một bài pipeline cá nhân; mục đích là ghi nhận ownership và bằng chứng đóng góp trong sản phẩm nhóm.

---

## Thông tin

- Họ và tên: Ninh Quang Minh
- Mã học viên: 2A202602432
- Nhóm: Top1Server
- Repository/branch: https://github.com/tungne1311/K4-L3A-RAG-Pipeline-Top1Server

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| R4 - Generation & UI | Viết hàm sinh câu trả lời bằng GPT-4o-mini (Task 10), thêm cơ chế Safe Refusal chống hallucination. | `src/task10_generation.py` | Done |
| R4 - Context Reordering | Code logic sắp xếp lại chunks `reorder_for_llm` để xử lý vấn đề "lost-in-the-middle". | `src/task10_generation.py` | Done |
| R4 - Chatbot UI | Build giao diện Chatbot bằng Streamlit, custom CSS (Glassmorphism, Dark/Light mode). | `app.py` | Done |
| R4 - Presentation | Làm slide HTML bằng Reveal.js chuẩn bị báo cáo. | `presentation/slide.html` | Done |
| R4 - Evaluation (Partial) | Phân khung 15 câu Q&A Golden Dataset và phân công mốc nộp cho R1-R3. | `group_project/evaluation/golden_dataset.json` | Partial |

Chỉ kê khai công việc có thể đối chiếu bằng file, commit, pull request, test hoặc kết quả evaluation.

## Quyết định kỹ thuật quan trọng

Mô tả tối đa hai quyết định mà bạn trực tiếp tham gia:

1. **Quyết định:** Tự động mock data (dữ liệu giả lập) trên tầng UI/Generation khi R1-R3 chưa xong task.  
   **Lý do/evidence:** Vì R4 nằm cuối pipeline, nếu đợi có dữ liệu ChromaDB/BM25 thật mới code UI thì sẽ không kịp deadline. Việc mock data giúp R4 hoàn thiện 100% app.py và code gọi LLM độc lập hoàn toàn.  
   **Trade-off:** Mất thêm chút thời gian code lớp Mock, và phải nhớ đổi hàm khi ghép API thật sau này.

2. **Quyết định:** Custom CSS giao diện Streamlit thay vì dùng mặc định.  
   **Lý do/evidence:** Giao diện Streamlit mặc định khá "basic". Đã tiêm mã HTML/CSS vào `st.markdown` để bo góc, đổi màu nền theo biến `--secondary-background-color` nhằm khắc phục lỗi khung trắng khi bật Dark Mode.  
   **Trade-off:** Code `app.py` dài hơn và nhìn hơi rối phần đầu do phải nhúng CSS thô.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: Test truy vấn ngoài luồng (VD: "Thời tiết Paris thế nào?").
- Kết quả trước/sau nếu có: Trước khi test LLM vẫn cố gắng trả lời hoặc bịa. Sau khi nhúng Safe Refusal, LLM lập tức trả về: "Tôi không thể xác minh thông tin này...".
- Lỗi đã phát hiện và cách xử lý: Lỗi giao diện hiển thị các block thẻ Nguồn (Source) bị nền trắng chói mắt khi user để Dark Mode. Xử lý bằng cách sửa toàn bộ mã HEX cứng thành biến CSS `var(--secondary-background-color)` và `var(--text-color)`.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Phần gọi LLM API hiện tại chỉ đang bắt luồng trả lời trực tiếp (sync), nếu sau này hệ thống mở rộng nhiều user thì có thể bị nghẽn mạng do gọi OpenAI API không dùng Async.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Chuyển đổi toàn bộ `app.py` sang sử dụng Streaming response (hiển thị chữ gõ từng từ ra màn hình) để UX được mượt hơn.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 20-09-2026
- Tên thành viên: Ninh Quang Minh
