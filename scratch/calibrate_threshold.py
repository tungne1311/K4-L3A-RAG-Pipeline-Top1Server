"""
Script hiệu chuẩn (Calibration) SCORE_THRESHOLD cho Pipeline Trợ lý du lịch Đà Nẵng – Hội An.

Cách thức hoạt động:
1. Sử dụng 10 query In-domain trích xuất trực tiếp từ 5 văn bản pháp lý Hội An/Cù Lao Chàm/Quảng Nam
   và 8 bài viết cẩm nang du lịch Đà Nẵng – Hội An do R1 thu thập.
2. Sử dụng 8 query Out-of-domain hoàn toàn ngoài lề (điện lạnh, toán học, y tế, IT, thủ tục quốc tế).
3. Gọi trực tiếp hàm semantic_search() (Task 5 của R2) để trích xuất Dense Cosine Similarity thực tế.
4. Gọi trực tiếp hàm retrieve() (Task 9 của R3) để kiểm tra xem hệ thống có kích hoạt Fallback hay không.
5. Tính toán phân phối điểm (Min, Max, Mean) và tự động xác định ngưỡng tối ưu SCORE_THRESHOLD.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Đảm bảo UTF-8 cho console
sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

load_dotenv()

from src.task5_semantic_search import semantic_search
from src.task9_retrieval_pipeline import retrieve

# 10 query In-domain bám sát chính xác corpus Hội An - Đà Nẵng của R1
IN_DOMAIN_QUERIES = [
    ("Quy định buôn bán hàng rong vỉa hè tại khu phố cổ Hội An như thế nào?", "Hàng rong vỉa hè"),
    ("Khu vực bảo vệ I của di sản văn hóa thế giới Đô thị cổ Hội An gồm những phạm vi nào?", "Di sản Hội An"),
    ("Các hoạt động nào bị nghiêm cấm trong phân khu bảo vệ nghiêm ngặt của Khu bảo tồn biển Cù Lao Chàm?", "Cù Lao Chàm"),
    ("Trách nhiệm quản lý và bảo vệ di tích lịch sử văn hóa trên địa bàn tỉnh Quảng Nam thuộc về ai?", "Di tích Quảng Nam"),
    ("Nhiệm vụ của Ban quản lý dự án di sản Hội An trong việc bảo tồn và tu bổ di tích?", "Phân công bảo tồn"),
    ("Giá vé tham quan các điểm di tích trong phố cổ Hội An hiện nay là bao nhiêu?", "Giá vé Hội An"),
    ("Những món ăn đặc sản nổi tiếng nhất định phải thử khi đến Hội An là gì?", "Ẩm thực Hội An"),
    ("Kinh nghiệm đi tour lặn biển ngắm san hô tại đảo Cù Lao Chàm?", "Lặn biển Cù Lao Chàm"),
    ("Lịch trình du lịch Đà Nẵng 3 ngày 2 đêm tham quan những điểm nào?", "Lịch trình Đà Nẵng"),
    ("Địa chỉ ăn mì Quảng và bánh tráng cuốn thịt heo ngon ở Đà Nẵng?", "Ẩm thực Đà Nẵng"),
]

# 8 query Out-of-domain hoàn toàn ngoài phạm vi corpus du lịch
OUT_OF_DOMAIN_QUERIES = [
    ("Cách sửa lỗi máy giặt inverter không cấp nước khi giặt?", "Sửa máy giặt"),
    ("Công thức nghiệm của phương trình vi phân tuyến tính thuần nhất bậc hai?", "Toán học"),
    ("Hướng dẫn cài đặt driver card đồ họa NVIDIA trên hệ điều hành Ubuntu 22.04?", "Cài đặt phần mềm"),
    ("Triệu chứng ban đầu và phương pháp phòng ngừa bệnh tiểu đường tuýp 2?", "Y tế sức khỏe"),
    ("Cách làm bánh pizza Margherita chuẩn hương vị truyền thống của Ý?", "Ẩm thực phương Tây"),
    ("Nguyên lý hoạt động của động cơ phản lực cánh quạt phản lực turbofan?", "Kỹ thuật hàng không"),
    ("Quy trình và thủ tục nộp hồ sơ xin visa định cư diện tay nghề tại Canada?", "Thủ tục xuất nhập cảnh"),
    ("Các bước giải khối Rubik 3x3 nâng cao bằng phương pháp CFOP?", "Trò chơi trí tuệ"),
]


def run_calibration():
    print("=" * 105)
    print("BẢNG HIỆU CHUẨN THỰC ĐO (CALIBRATION TABLE) — DỰ ÁN TRỢ LÝ DU LỊCH ĐÀ NẴNG – HỘI AN")
    print("=" * 105)
    print(f"{'STT':<4} | {'Chủ đề':<22} | {'Loại':<13} | {'Dense Top-1':<11} | {'Fallback?':<9} | {'Method':<10} | {'Query'}")
    print("-" * 105)

    in_records = []
    for idx, (q, topic) in enumerate(IN_DOMAIN_QUERIES, start=1):
        dense_results = semantic_search(q, top_k=1)
        score = float(dense_results[0]["score"]) if dense_results else 0.0
        
        pipeline_results = retrieve(q, top_k=3)
        method = pipeline_results[0]["retrieval_method"] if pipeline_results else "none"
        is_fallback = (method == "pageindex")
        
        in_records.append(score)
        print(f"{idx:<4} | {topic:<22} | {'In-domain':<13} | {score:<11.4f} | {'Có' if is_fallback else 'Không':<9} | {method:<10} | {q[:35]}...")

    print("-" * 105)
    out_records = []
    for idx, (q, topic) in enumerate(OUT_OF_DOMAIN_QUERIES, start=1):
        dense_results = semantic_search(q, top_k=1)
        score = float(dense_results[0]["score"]) if dense_results else 0.0
        
        pipeline_results = retrieve(q, top_k=3)
        method = pipeline_results[0]["retrieval_method"] if pipeline_results else "none"
        is_fallback = (method == "pageindex")
        
        out_records.append(score)
        print(f"{idx+10:<4} | {topic:<22} | {'Out-domain':<13} | {score:<11.4f} | {'Có' if is_fallback else 'Không':<9} | {method:<10} | {q[:35]}...")

    print("=" * 105)
    
    avg_in = sum(in_records) / len(in_records) if in_records else 0.0
    min_in = min(in_records) if in_records else 0.0
    max_in = max(in_records) if in_records else 0.0

    avg_out = sum(out_records) / len(out_records) if out_records else 0.0
    min_out = min(out_records) if out_records else 0.0
    max_out = max(out_records) if out_records else 0.0

    # Tính toán ngưỡng phân định
    if min_in > max_out:
        optimal_thresh = round((min_in + max_out) / 2, 2)
    else:
        optimal_thresh = 0.40

    print("KẾT QUẢ THỰC NGHIỆM ĐO ĐẠC:")
    print(f"  • In-domain  (10 queries): Min = {min_in:.4f} | Max = {max_in:.4f} | Mean = {avg_in:.4f}")
    print(f"  • Out-domain (8 queries) : Min = {min_out:.4f} | Max = {max_out:.4f} | Mean = {avg_out:.4f}")
    print(f"  • Khoảng phân tách (Separation Margin): {min_in - max_out:.4f}")
    print(f"\n👉 NGƯỠNG TỐI ƯU ĐÃ CHỐT: SCORE_THRESHOLD = {optimal_thresh:.2f}")
    print(f"👉 Hãy đảm bảo file .env có dòng: SCORE_THRESHOLD={optimal_thresh:.2f}")
    print("=" * 105)


if __name__ == "__main__":
    run_calibration()
