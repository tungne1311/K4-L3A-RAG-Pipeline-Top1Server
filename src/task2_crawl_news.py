"""
Task 2 — Crawl bài viết/thông báo về du lịch Đà Nẵng – Hội An.

Nguồn ưu tiên cổng thông tin chính thức (danang.gov.vn,
danangfantasticity.com) và báo chí chính thống (baodanang.vn,
baovanhoa.vn). Mỗi bài lưu thành một JSON trong data/landing/news/ với
đủ url, title, date_crawled, content_markdown.

Chiến lược crawl:
    1. Thử Crawl4AI (headless Chromium) trước.
    2. Nếu Crawl4AI/Playwright không sẵn sàng hoặc trả nội dung quá ngắn,
       fallback sang requests + BeautifulSoup rồi tự chuyển sang Markdown.

Fallback tồn tại vì toàn bộ nguồn trên đều render server-side: bản HTML
thuần đã đủ nội dung, không cần trình duyệt. Nhờ vậy corpus vẫn hoàn chỉnh
trên máy chưa chạy `playwright install chromium`.
"""

from __future__ import annotations

import asyncio
import json
import re

import sys

# Console Windows mặc định dùng cp1252, không in được tiếng Việt.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 45
MIN_CONTENT_CHARS = 400

ARTICLE_URLS = [
    "https://danang.gov.vn/vi/w/quy-dinh-muc-thu-10000-40000-dong-luot-tham-quan-tai-hoi-an-my-son-va-cac-thap-co",
    "https://baodanang.vn/phi-tham-quan-10-000-40-000-dong-luot-tai-hoi-an-my-son-va-cac-thap-co-3324679.html",
    "https://baodanang.vn/du-lich-da-nang-san-sang-but-pha-nam-2026-3317870.html",
    "https://danangfantasticity.com/tin-tuc/da-nang-don-gan-98-trieu-luot-khach-trong-6-thang-dau-nam-2026",
    "https://danangfantasticity.com/tin-tuc/diem-danh-cac-san-pham-du-lich-moi-tai-da-nang-2026",
    "https://baovanhoa.vn/du-lich/da-nang-don-song-khach-he-2026-229729.html",
    "https://baovanhoa.vn/du-lich/du-lich-da-nang-khoi-sac-ngay-tu-dau-nam-2026-202394.html",
    "https://baotuyenquang.com.vn/du-lich/202602/pho-co-hoi-an-tam-dung-ban-ve-tham-quan-dip-tet-binh-ngo-2026-6202399/",
]

# Thẻ điều hướng/quảng cáo cần loại trước khi lấy nội dung.
JUNK_TAGS = [
    "script", "style", "noscript", "nav", "header", "footer",
    "aside", "form", "iframe", "svg", "button",
]

# Thứ tự ưu tiên khi tìm khối nội dung chính của bài.
CONTENT_SELECTORS = [
    "article",
    "[itemprop='articleBody']",
    ".journal-content-article",
    ".detail-content",
    ".article-content",
    ".entry-content",
    ".post-content",
    ".content-detail",
    "#main-detail",
    "main",
]

HEADING_PATTERN = re.compile(r"^h([1-6])$")


def _clean_soup(soup: BeautifulSoup) -> None:
    for tag_name in JUNK_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()


def _extract_title(soup: BeautifulSoup) -> str:
    meta = soup.find("meta", attrs={"property": "og:title"})
    if meta and meta.get("content", "").strip():
        return meta["content"].strip()
    if soup.h1 and soup.h1.get_text(strip=True):
        return soup.h1.get_text(" ", strip=True)
    if soup.title and soup.title.get_text(strip=True):
        return soup.title.get_text(" ", strip=True).split("|")[0].strip()
    return "Unknown"


def _node_to_markdown(root) -> str:
    """Chuyển khối nội dung sang Markdown, bỏ trùng lặp do lồng thẻ."""
    lines: list[str] = []
    seen: set[str] = set()

    for element in root.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote", "figcaption"]
    ):
        text = " ".join(element.get_text(" ", strip=True).split())
        if len(text) < 2 or text in seen:
            continue
        seen.add(text)

        heading = HEADING_PATTERN.match(element.name)
        if heading:
            lines.append(f"{'#' * int(heading.group(1))} {text}")
        elif element.name == "li":
            lines.append(f"- {text}")
        elif element.name == "blockquote":
            lines.append(f"> {text}")
        else:
            lines.append(text)

    return "\n\n".join(lines)


def _html_to_article(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    _clean_soup(soup)

    best = ""
    for selector in CONTENT_SELECTORS:
        node = soup.select_one(selector)
        if node is None:
            continue
        markdown = _node_to_markdown(node)
        if len(markdown) > len(best):
            best = markdown
        if len(best) >= MIN_CONTENT_CHARS:
            break

    if len(best) < MIN_CONTENT_CHARS and soup.body is not None:
        best = _node_to_markdown(soup.body)

    return {
        "url": url,
        "title": _extract_title(soup),
        "date_crawled": date.today().isoformat(),
        "content_markdown": best,
    }


def _fetch_with_requests(url: str) -> dict:
    response = requests.get(
        url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    response.encoding = response.apparent_encoding or response.encoding
    return _html_to_article(url, response.text)


async def _fetch_with_crawl4ai(url: str) -> dict | None:
    """Trả về None khi Crawl4AI không dùng được, để gọi fallback."""
    try:
        from crawl4ai import AsyncWebCrawler
    except ImportError:
        return None

    try:
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url)
            markdown = str(getattr(result, "markdown", "") or "")
            if len(markdown) < MIN_CONTENT_CHARS:
                return None
            metadata = getattr(result, "metadata", None) or {}
            return {
                "url": url,
                "title": metadata.get("title") or "Unknown",
                "date_crawled": date.today().isoformat(),
                "content_markdown": markdown,
            }
    except Exception as error:
        print(f"  crawl4ai unavailable ({type(error).__name__}), using requests")
        return None


async def crawl_article(url: str) -> dict:
    """Crawl một URL và trả về dict đủ 4 field bắt buộc."""
    article = await _fetch_with_crawl4ai(url)
    if article is None:
        article = _fetch_with_requests(url)

    if len(article["content_markdown"]) < MIN_CONTENT_CHARS:
        raise ValueError(
            f"content too short ({len(article['content_markdown'])} chars)"
        )
    if not article["title"].strip() or article["title"] == "Unknown":
        raise ValueError("missing article title")
    return article


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    saved = 0

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            saved += 1
            print(
                f"Saved: {output.name} — {len(article['content_markdown']):,} chars "
                f"— {article['title'][:60]}"
            )
        except Exception as error:
            print(f"Failed: {url} — {type(error).__name__}: {error}")

    print(f"\nSaved {saved}/{len(ARTICLE_URLS)} articles into {DATA_DIR}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
