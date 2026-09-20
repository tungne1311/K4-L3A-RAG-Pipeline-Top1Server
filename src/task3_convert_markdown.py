"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

    - Văn bản pháp quy (PDF/DOC/DOCX)  -> data/standardized/legal/*.md
    - Bài viết đã crawl (JSON)         -> data/standardized/news/*.md

Mỗi file Markdown mở đầu bằng khối metadata (title, source, doc_type, url)
để Task 4 lấy được nguồn và Task 10 dựng citation kiểm chứng được.

Chạy lại nhiều lần không tạo file trùng: tên file output suy ra từ tên file
input nên lần chạy sau ghi đè đúng file cũ.
"""

from __future__ import annotations

import json
import re

import sys

# Console Windows mặc định dùng cp1252, không in được tiếng Việt.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path

from markitdown import MarkItDown

from .task1_collect_legal_docs import SOURCES as LEGAL_SOURCES


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"
MANIFEST_PATH = Path(__file__).parent.parent / "data" / "SOURCES.md"

LEGAL_SUFFIXES = {".pdf", ".doc", ".docx"}
MIN_CHARS = 200

_BLANK_LINES = re.compile(r"\n{3,}")
_TRAILING_SPACES = re.compile(r"[ \t]+\n")
# PDF căn đều lề khiến pdfminer chèn nhiều space giữa các từ.
_MULTI_SPACES = re.compile(r"[ \t]{2,}")


def _normalise(text: str) -> str:
    """Bỏ khoảng trắng thừa để chunking không sinh chunk rỗng."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _MULTI_SPACES.sub(" ", text)
    text = _TRAILING_SPACES.sub("\n", text)
    return _BLANK_LINES.sub("\n\n", text).strip()


def _header(title: str, source: str, doc_type: str, url: str, extra: str = "") -> str:
    lines = [
        f"# {title}",
        "",
        f"**Source:** {source}",
        f"**Doc type:** {doc_type}",
        f"**URL:** {url}",
    ]
    if extra:
        lines.append(extra)
    lines += ["", "---", ""]
    return "\n".join(lines)


def convert_legal_docs() -> int:
    """Convert PDF/DOC/DOCX trong landing/legal sang standardized/legal."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    converter = MarkItDown()
    converted = 0

    for path in sorted(legal_dir.iterdir()):
        if path.suffix.lower() not in LEGAL_SUFFIXES:
            continue

        meta = LEGAL_SOURCES.get(path.name, {})
        try:
            body = _normalise(converter.convert(str(path)).text_content)
        except Exception as error:
            print(f"Skip {path.name}: {type(error).__name__} — {error}")
            continue

        if len(body) < MIN_CHARS:
            print(f"Skip {path.name}: chỉ trích được {len(body)} ký tự (PDF scan?)")
            continue

        title = meta.get("title") or path.stem.replace("-", " ")
        header = _header(
            title=title,
            source=path.name,
            doc_type="legal",
            url=meta.get("url", "N/A"),
            extra=f"**Issuer:** {meta['issuer']}" if meta.get("issuer") else "",
        )
        (output_dir / f"{path.stem}.md").write_text(header + body, encoding="utf-8")
        converted += 1
        print(f"Converted: {path.name} -> {path.stem}.md ({len(body):,} chars)")

    return converted


def convert_news_articles() -> int:
    """Convert JSON trong landing/news sang standardized/news."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    converted = 0

    for path in sorted(news_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        body = _normalise(data.get("content_markdown", ""))

        if len(body) < MIN_CHARS:
            print(f"Skip {path.name}: nội dung chỉ {len(body)} ký tự")
            continue

        header = _header(
            title=data.get("title", path.stem),
            source=path.name,
            doc_type="news",
            url=data.get("url", "N/A"),
            extra=f"**Crawled:** {data.get('date_crawled', 'N/A')}",
        )
        (output_dir / f"{path.stem}.md").write_text(header + body, encoding="utf-8")
        converted += 1
        print(f"Converted: {path.name} -> {path.stem}.md ({len(body):,} chars)")

    return converted


def write_source_manifest() -> None:
    """Sinh danh sách nguồn để nhóm đối chiếu citation (R4 dùng)."""
    rows = ["# Danh sách nguồn — Du lịch Đà Nẵng – Hội An", ""]

    rows += ["## Văn bản chính sách / quy định", "",
             "| File | Tiêu đề | Cơ quan ban hành | URL |",
             "| --- | --- | --- | --- |"]
    for path in sorted((LANDING_DIR / "legal").iterdir()):
        if path.suffix.lower() not in LEGAL_SUFFIXES:
            continue
        meta = LEGAL_SOURCES.get(path.name, {})
        rows.append(
            f"| `{path.name}` | {meta.get('title', path.stem)} | "
            f"{meta.get('issuer', 'N/A')} | {meta.get('url', 'N/A')} |"
        )

    rows += ["", "## Bài viết / trang tin", "",
             "| File | Tiêu đề | Ngày thu thập | URL |",
             "| --- | --- | --- | --- |"]
    for path in sorted((LANDING_DIR / "news").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            f"| `{path.name}` | {data.get('title', '')} | "
            f"{data.get('date_crawled', '')} | {data.get('url', '')} |"
        )

    MANIFEST_PATH.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote source manifest: {MANIFEST_PATH}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing và ghi danh sách nguồn."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    legal = convert_legal_docs()
    news = convert_news_articles()
    write_source_manifest()
    print(f"\nStandardized {legal} legal + {news} news files into {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
