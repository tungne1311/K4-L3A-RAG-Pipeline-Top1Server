# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-20 |
| Framework and version              | RAGAS 0.4.3 |
| Evaluator model                    | gpt-4o-mini |
| Generator model                    | gpt-4o-mini |
| Embedding model                    | BAAI/bge-m3 |
| Corpus version/commit              | 574 chunks (13 docs) |
| Golden dataset size                | 15 Q&A pairs |
| 	op_k                            | 5 |
| Fallback threshold and calibration | 0.40 (Hiệu chuẩn thực nghiệm Dense Cosine score trên 10 query in-domain Hội An - Đà Nẵng và 8 query out-of-domain) |

## Configurations

- **Config A – dense-only:** Sử dụng Dense Search (BAAI/bge-m3), không dùng RRF, không dùng BM25.
- **Config B – hybrid + RRF:** Kết hợp Dense và Lexical (BM25) thông qua thuật toán RRF.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và 	op_k; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |    0.880 |    0.940 |    +0.060 |
| Answer relevance  |    0.920 |    0.950 |    +0.030 |
| Context recall    |    0.820 |    0.910 |    +0.090 |
| Context precision |    0.850 |    0.890 |    +0.040 |
| **Average**       |  **0.867** |  **0.922** |  **+0.055** |

## A/B comparison

- Cấu hình tốt hơn: **Config B (Hybrid + RRF)**
- Evidence: Điểm trung bình tăng 0.055. Đặc biệt Context Recall tăng mạnh nhất (+0.090) do BM25 bắt được các từ khóa hiếm/chính xác (như số hiệu nghị định, từ lóng địa phương) mà Dense search có thể bỏ qua.
- Trade-off về latency/cost: Config B tốn thêm thời gian thực thi thuật toán BM25 và RRF (khoảng 100-200ms) trên mỗi truy vấn, nhưng không làm tăng chi phí API do BM25 chạy cục bộ.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Chi phí tham gia tour Cù Lao Chàm? | Config A | 0.85 | 0.80 | 0.60 | 0.70 | retrieval | Dense search trả về các gói tour chung chung thay vì giá cụ thể cho Cù Lao Chàm. |
|   2 | Quyết định 123/QĐ-UBND về du lịch Hội An ban hành năm nào? | Config A | 0.90 | 0.85 | 0.50 | 0.60 | retrieval | Dense search không nhạy bén với các con số quyết định pháp lý cụ thể. |
|   3 | Làm sao để sửa máy lạnh inverter bị chảy nước? | Config B | 1.00 | 0.50 | 0.00 | 0.00 | generation | Câu hỏi Out-of-domain bị Fallback từ chối, do đó Relevance với context bằng 0. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Bật Hybrid Search mặc định | Config B vượt trội Config A ở tất cả các chỉ số, đặc biệt Context Recall | Tăng độ chính xác khi truy vấn từ khóa pháp lý/địa danh | Chạy lại tập Golden Dataset để xác nhận |
|        2 | Tinh chỉnh BM25 weights | Các câu hỏi chứa số hiệu pháp lý vẫn bị thỉnh thoảng trượt top 1 | Tăng Context Precision lên >0.90 | Thử nghiệm với alpha (0.3 đến 0.7) trong RRF |
|        3 | Nâng cấp Generator | Mô hình gpt-4o-mini đôi khi vẫn sinh câu trả lời hơi dài dòng | Cải thiện Answer Relevance | Đo lại bằng RAGAS với gpt-4o (nếu có ngân sách) |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Tăng chunk overlap lên 100 | Config B | +0.010 Recall | Tăng nhẹ size DB | Đáng để cân nhắc nếu cần bắt ngữ cảnh rộng hơn. |