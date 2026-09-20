"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Đề tài nhóm: Du lịch Đà Nẵng – Hội An.

Nguồn: kho văn bản pháp quy của Trung tâm Quản lý Bảo tồn Di sản Văn hóa
Hội An (hoianheritage.net) — cơ quan trực tiếp quản lý Khu phố cổ Hội An.
Mỗi tài liệu đều là văn bản do UBND tỉnh Quảng Nam hoặc UBND TP Hội An ban
hành, có số hiệu và ngày ban hành kiểm chứng được.

Lưu ý kỹ thuật: server hoianheritage.net hay đóng kết nối giữa chừng nên
file tải về bị cắt (thiếu %%EOF). download_documents() vì vậy tải theo kiểu
resume (HTTP Range) và chỉ chấp nhận file đã toàn vẹn.
"""

from __future__ import annotations

import time
from pathlib import Path

import requests


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 90
MAX_ATTEMPTS = 6
MIN_BYTES = 1024

_BASE = "https://hoianheritage.net/vi/laws/detail"

# filename -> metadata. Filename không dấu, phản ánh đúng nội dung văn bản.
SOURCES: dict[str, dict[str, str]] = {
    "quyche-bao-ve-di-san-the-gioi-pho-co-hoi-an.pdf": {
        "url": f"{_BASE}/Quy-che-bao-ve-Di-san-van-hoa-the-gioi-Khu-pho-co-Hoi-An-13.html?download=1&id=0",
        "title": "Quy chế bảo vệ Di sản văn hóa thế giới Khu phố cổ Hội An",
        "issuer": "UBND tỉnh Quảng Nam",
    },
    # Lưu ý: QĐ 351/QĐ-UBND (Kế hoạch quản lý di sản 2020-2025) đã bị loại
    # khỏi corpus vì bản PDF công bố là bản scan, không có text layer.
    "quyche-quan-ly-bao-ve-di-tich-quang-nam.pdf": {
        "url": f"{_BASE}/Ban-hanh-Quy-che-ve-quan-ly-bao-ve-va-phat-huy-gia-tri-di-tich-lich-su-van-hoa-va-danh-lam-thang-canh-tren-dia-ban-tinh-Quang-Nam-12.html?download=1&id=0",
        "title": "Quy chế quản lý, bảo vệ và phát huy giá trị di tích lịch sử - văn hóa và danh lam thắng cảnh trên địa bàn tỉnh Quảng Nam",
        "issuer": "UBND tỉnh Quảng Nam",
    },
    "quyche-quan-ly-khu-bao-ton-bien-cu-lao-cham.pdf": {
        "url": f"{_BASE}/Ban-hanh-Quy-che-quan-ly-Khu-bao-ton-bien-Cu-Lao-Cham-14.html?download=1&id=0",
        "title": "Quy chế quản lý Khu bảo tồn biển Cù Lao Chàm",
        "issuer": "UBND tỉnh Quảng Nam",
    },
    "de-an-buon-ban-hang-rong-via-he-pho-co-hoi-an.pdf": {
        "url": f"{_BASE}/De-an-Bo-tri-buon-ban-hang-rong-via-he-trong-khu-pho-co-Hoi-An-9.html?download=1&id=0",
        "title": "Đề án bố trí buôn bán hàng rong, vỉa hè trong Khu phố cổ Hội An",
        "issuer": "UBND thành phố Hội An",
    },
    "quy-dinh-phan-cong-thuc-hien-quyche-bao-ve-di-san-hoi-an.pdf": {
        "url": f"{_BASE}/Quy-dinh-phan-cong-nhiem-vu-thuc-hien-quy-che-bao-ve-di-san-van-hoa-the-gioi-Khu-Pho-Co-Hoi-An-16.html?download=1&id=0",
        "title": "Quy định phân công nhiệm vụ thực hiện Quy chế bảo vệ Di sản văn hóa thế giới Khu phố cổ Hội An",
        "issuer": "UBND thành phố Hội An",
    },
}


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def _is_complete(path: Path) -> bool:
    """Kiểm tra file tải về đã toàn vẹn chưa."""
    if not path.exists() or path.stat().st_size < MIN_BYTES:
        return False
    head = path.read_bytes()[:8]
    if path.suffix.lower() == ".pdf":
        if not head.startswith(b"%PDF"):
            return False
        with path.open("rb") as handle:
            handle.seek(max(0, path.stat().st_size - 4096))
            return b"%%EOF" in handle.read()
    # .doc (OLE2) và .docx (ZIP) không có marker kết thúc rõ ràng.
    return head.startswith(b"\xd0\xcf\x11\xe0") or head.startswith(b"PK\x03\x04")


def _download_with_resume(url: str, target: Path) -> bool:
    """Tải file, tự resume khi server ngắt kết nối giữa chừng."""
    previous_delta = 0
    for attempt in range(1, MAX_ATTEMPTS + 1):
        downloaded = target.stat().st_size if target.exists() else 0
        headers = {"User-Agent": USER_AGENT}
        mode = "wb"
        if downloaded:
            headers["Range"] = f"bytes={downloaded}-"
            mode = "ab"

        try:
            with requests.get(
                url, headers=headers, timeout=REQUEST_TIMEOUT, stream=True
            ) as response:
                if response.status_code != 416:
                    response.raise_for_status()
                    # Server bỏ qua Range -> phải ghi lại từ đầu.
                    if response.status_code == 200 and mode == "ab":
                        mode = "wb"
                    with target.open(mode) as handle:
                        for chunk in response.iter_content(65536):
                            handle.write(chunk)
        except requests.RequestException as error:
            print(f"  attempt {attempt}: {type(error).__name__} — {error}")

        if _is_complete(target):
            print(f"  attempt {attempt}: complete ({target.stat().st_size:,} bytes)")
            return True
        size = target.stat().st_size if target.exists() else 0
        print(f"  attempt {attempt}: partial ({size:,} bytes)")

        # Một số server trả 206 nhưng vẫn gửi lại từ đầu: file chỉ phình ra
        # mà không bao giờ đủ. Phát hiện bằng delta lặp lại và tải lại từ 0.
        delta = size - downloaded
        if delta and delta == previous_delta and target.exists():
            print("  server ignores Range offset — restarting from scratch")
            target.unlink()
            previous_delta = 0
        else:
            previous_delta = delta
        time.sleep(min(2 * attempt, 8))

    return False


def download_documents() -> None:
    """Tải các văn bản chính sách vào data/landing/legal/."""
    setup_directory()
    failures: list[str] = []

    for filename, meta in SOURCES.items():
        target = DATA_DIR / filename
        if _is_complete(target):
            print(f"Skip (already complete): {filename}")
            continue
        print(f"Downloading: {filename}")
        if not _download_with_resume(meta["url"], target):
            failures.append(filename)
            if target.exists():
                target.unlink()

    complete = [name for name in SOURCES if _is_complete(DATA_DIR / name)]
    print(f"\nDownloaded {len(complete)}/{len(SOURCES)} documents into {DATA_DIR}")
    if failures:
        print(f"Failed: {', '.join(failures)}")


if __name__ == "__main__":
    download_documents()
