"""Scrape a docs site into Markdown files.

This script prefers sitemap discovery and falls back to a bounded recursive crawl.

Recommended invocation:

    uv run python scripts/scrape_docs.py \
      https://docs.battlecode.cam \
      --output-dir scraped-docs
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urldefrag, urljoin, urlparse
from xml.etree import ElementTree

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_markdown


DEFAULT_TIMEOUT = 20.0
MAX_CRAWL_PAGES = 200
DEFAULT_ROOT_URL = "https://docs.battlecode.cam"


@dataclass(slots=True)
class Page:
    url: str
    title: str
    markdown: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape a docs site into readable Markdown files."
    )
    parser.add_argument(
        "root_url",
        nargs="?",
        default=DEFAULT_ROOT_URL,
        help=f"Root docs URL. Defaults to {DEFAULT_ROOT_URL}.",
    )
    parser.add_argument(
        "--output-dir",
        default="scraped-docs",
        help="Directory to write per-page markdown and the combined corpus.",
    )
    parser.add_argument(
        "--combined-name",
        default="all-pages.md",
        help="Filename for the combined corpus inside output-dir.",
    )
    parser.add_argument(
        "--max-crawl-pages",
        type=int,
        default=MAX_CRAWL_PAGES,
        help="Fallback crawl cap when no sitemap is available.",
    )
    return parser.parse_args()


def normalize_url(url: str) -> str:
    clean, _fragment = urldefrag(url)
    parsed = urlparse(clean)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return parsed._replace(scheme=scheme, netloc=netloc, path=path, fragment="").geturl()


def same_site(url: str, root_url: str) -> bool:
    a = urlparse(url)
    b = urlparse(root_url)
    return a.netloc == b.netloc and a.scheme in {"http", "https"}


def fetch_text(client: httpx.Client, url: str) -> str:
    response = client.get(url, follow_redirects=True, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    return response.text


def discover_urls(client: httpx.Client, root_url: str, max_crawl_pages: int) -> list[str]:
    root_url = normalize_url(root_url)

    try:
        sitemap_url = urljoin(root_url + "/", "sitemap.xml")
        sitemap_xml = fetch_text(client, sitemap_url)
        root = ElementTree.fromstring(sitemap_xml)
        urls = [
            normalize_url(node.text)
            for node in root.findall(".//{*}loc")
            if node.text and same_site(node.text, root_url)
        ]
    except Exception:
        urls = []

    urls = [url for url in urls if same_site(url, root_url)]
    if urls:
        return sorted(dict.fromkeys(urls))

    return crawl_urls(client, root_url, max_pages=max_crawl_pages)


def crawl_urls(client: httpx.Client, root_url: str, max_pages: int) -> list[str]:
    queue: deque[str] = deque([normalize_url(root_url)])
    seen: set[str] = set()
    discovered: list[str] = []

    while queue and len(discovered) < max_pages:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)

        try:
            html = fetch_text(client, url)
        except Exception:
            continue

        discovered.append(url)
        soup = BeautifulSoup(html, "html.parser")
        for anchor in soup.select("a[href]"):
            href = anchor.get("href")
            if not href:
                continue
            child = normalize_url(urljoin(url, href))
            if same_site(child, root_url) and child not in seen:
                queue.append(child)

    return discovered


def best_title(html: str, url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        title = re.sub(r"[ \t]+", " ", soup.title.string).strip()
        title = re.sub(r"\s*-\s*Cambridge Battlecode\s*$", "", title)
        return title
    return urlparse(url).path.strip("/") or "index"


def is_definitely_ui_line(line: str) -> bool:
    return line.strip() in {
        "Copy",
        "Ask AI",
        "Search...",
        "Skip to main content",
    }


def clean_markdown(markdown: str) -> str:
    markdown = markdown.replace("\u200b", "")
    markdown = re.sub(r"\[\s*\]\(#.*?\)", "", markdown)
    markdown = re.sub(r"\[(?:¶|§)\]\(#.*?\)", "", markdown)
    markdown = re.sub(r"^\s*\[\]\(#.*?\)\s*$", "", markdown, flags=re.MULTILINE)
    cleaned: list[str] = []
    blank_run = 0

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or is_definitely_ui_line(line):
            blank_run += 1
            if blank_run <= 1:
                cleaned.append("")
            continue

        blank_run = 0
        cleaned.append(line)

    return "\n".join(cleaned).strip()


def strip_prelude(markdown: str) -> str:
    lines = markdown.splitlines()
    first_h1 = next((i for i, line in enumerate(lines[:30]) if line.startswith("# ")), None)
    if first_h1 is not None:
        lines = lines[first_h1 + 1 :]
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).strip()


def extract_markdown(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find(id="content-area") or soup.body
    if content is None:
        return None

    for tag in content.select(
        "script, style, noscript, svg, button, form, input, textarea, footer, a.group.w-full"
    ):
        tag.decompose()

    markdown = html_to_markdown(
        str(content),
        heading_style="ATX",
        bullets="-",
        strip=["img"],
    )
    markdown = clean_markdown(markdown)
    markdown = strip_prelude(markdown)
    return markdown or None


def slug_for_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return "index"
    slug = path.replace("/", "__")
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", slug)
    return slug or "page"


def page_header(page: Page) -> str:
    return "\n".join(
        [
            f"Title: {page.title}",
            "",
            f"Source: {page.url}",
            "",
            "---",
        ]
    )


def render_page(page: Page) -> str:
    return f"{page_header(page)}\n\n{page.markdown.strip()}\n"


def write_outputs(output_dir: Path, combined_name: str, pages: Iterable[Page]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = list(pages)
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    index_lines = ["# Docs", "", "## Pages", ""]
    combined_parts: list[str] = []

    for page in pages:
        slug = slug_for_url(page.url)
        relative_path = f"pages/{slug}.md"
        page_path = pages_dir / f"{slug}.md"
        page_path.write_text(render_page(page), encoding="utf-8")

        index_lines.append(f"- [{page.title}]({relative_path})")
        combined_parts.extend(
            [
                render_page(page).strip(),
                "",
                "---",
                "",
            ]
        )

    (output_dir / "README.md").write_text("\n".join(index_lines).strip() + "\n", encoding="utf-8")
    (output_dir / combined_name).write_text(
        "\n".join(combined_parts[:-2]).strip() + "\n", encoding="utf-8"
    )


def scrape(root_url: str, output_dir: Path, combined_name: str, max_crawl_pages: int) -> int:
    root_url = normalize_url(root_url)
    with httpx.Client(
        headers={"User-Agent": "battlecode-doc-scraper/1.0"},
        follow_redirects=True,
    ) as client:
        urls = discover_urls(client, root_url, max_crawl_pages=max_crawl_pages)
        print(f"Discovered {len(urls)} pages from {root_url}")
        pages: list[Page] = []

        for index, url in enumerate(urls, start=1):
            print(f"[{index}/{len(urls)}] Fetching {url}")
            try:
                html = fetch_text(client, url)
            except Exception as exc:
                print(f"[warn] failed to fetch {url}: {exc}", file=sys.stderr)
                continue

            markdown = extract_markdown(html)
            if not markdown:
                print(f"[warn] failed to extract readable markdown for {url}", file=sys.stderr)
                continue

            title = best_title(html, url)
            print(f"[{index}/{len(urls)}] Processed {title}")
            pages.append(
                Page(
                    url=url,
                    title=title,
                    markdown=markdown,
                )
            )

    pages.sort(key=lambda page: page.url)
    write_outputs(output_dir, combined_name, pages)
    print(f"Wrote {len(pages)} pages to {output_dir}")
    print(f"Combined corpus: {output_dir / combined_name}")
    return 0


def main() -> int:
    args = parse_args()
    return scrape(
        root_url=args.root_url,
        output_dir=Path(args.output_dir),
        combined_name=args.combined_name,
        max_crawl_pages=args.max_crawl_pages,
    )


if __name__ == "__main__":
    raise SystemExit(main())
