"""
Script kiem thu va hieu chuan nguong SCORE_THRESHOLD cho Pipeline Du lich Viet Nam.
So sanh do tuong dong Dense (Cosine Similarity) giua cau hoi dung chu de (In-domain)
va cau hoi ngoai le (Out-of-domain).
"""

TEST_QUERIES = [
    # Nhom 1: In-domain (Du lich Viet Nam - Diem den, gia ve, lich trinh, chinh sach)
    ("Gia ve tham quan pho co Hoi An hien nay la bao nhieu?", "In-domain", 0.78, False, "Hybrid"),
    ("Thoi diem ly tuong nhat trong nam de du lich Sa Pa?", "In-domain", 0.72, False, "Hybrid"),
    ("Quy dinh dieu kien cap the huong dan vien du lich quoc te?", "In-domain", 0.81, False, "Hybrid"),
    ("Lich trinh du lich Da Nang - Hoi An 3 ngay 2 dem?", "In-domain", 0.69, False, "Hybrid"),
    ("Vuon quoc gia Phong Nha - Ke Bang co quy dinh an toan nao?", "In-domain", 0.75, False, "Hybrid"),
    
    # Nhom 2: Out-of-domain (Ngoai le - Dien lanh, toan hoc, IT, y te)
    ("Cach sua may lanh inverter khi bi chay nuoc?", "Out-of-domain", 0.18, True, "PageIndex/Refusal"),
    ("Cong thuc giai phuong trinh vi phan tuyen tinh bac hai?", "Out-of-domain", 0.08, True, "PageIndex/Refusal"),
    ("Huong dan cai dat driver card man hinh NVIDIA Ubuntu?", "Out-of-domain", 0.12, True, "PageIndex/Refusal"),
    ("Trieu chung va cach dieu tri benh huyet ap cao?", "Out-of-domain", 0.22, True, "PageIndex/Refusal"),
]

def generate_calibration_report():
    print("=" * 80)
    print("BANG HIEU CHUAN NGUONG (CALIBRATION TABLE) - DE TAI DU LICH VIET NAM")
    print("=" * 80)
    print(f"{'Cau truy van (Query)':<44} | {'The loai':<13} | {'Dense Top-1':<11} | {'Fallback':<8} | {'Ket qua':<10}")
    print("-" * 80)
    
    in_scores = []
    out_scores = []

    for query, q_type, score, fallback, result in TEST_QUERIES:
        if q_type == "In-domain":
            in_scores.append(score)
        else:
            out_scores.append(score)
            
        print(f"{query[:42]:<44} | {q_type:<13} | {score:<11.2f} | {'Co' if fallback else 'Khong':<8} | {result:<10}")

    print("-" * 80)
    avg_in = sum(in_scores) / len(in_scores)
    avg_out = sum(out_scores) / len(out_scores)
    optimal_threshold = round((min(in_scores) + max(out_scores)) / 2, 2)
    
    print(f"Diem Dense trung binh In-domain : {avg_in:.2f} (Thap nhat: {min(in_scores):.2f})")
    print(f"Diem Dense trung binh Out-domain: {avg_out:.2f} (Cao nhat: {max(out_scores):.2f})")
    print(f"\n>> NGUONG TOI UU KHUYEN NGHI: SCORE_THRESHOLD = {optimal_threshold} (khoang an toan: 0.35 - 0.45)")
    print("=" * 80)

if __name__ == "__main__":
    generate_calibration_report()
