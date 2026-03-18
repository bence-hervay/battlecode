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

import httpx
import trafilatura
from bs4 import BeautifulSoup
from trafilatura.sitemaps import sitemap_search


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
        urls = [normalize_url(url) for url in sitemap_search(root_url)]
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


def is_heading(line: str) -> bool:
    return bool(re.match(r"^#{1,6}\s", line))


def is_list_item(line: str) -> bool:
    return bool(re.match(r"^(\s*[-*+]\s|\s*\d+\.\s)", line))


def is_table_line(line: str) -> bool:
    return line.count("|") >= 2 or bool(re.match(r"^\|?[-: ]+\|[-|: ]*$", line))


def is_block_line(line: str) -> bool:
    stripped = line.strip()
    return (
        is_heading(line)
        or is_list_item(line)
        or is_table_line(line)
        or stripped.startswith("```")
        or stripped.startswith("> ")
        or stripped == "---"
    )


def fix_inline_spacing(line: str) -> str:
    line = re.sub(r"\s+([,.;:)])", r"\1", line)
    line = re.sub(r"(`[^`]+`)\s+([,.;:)])", r"\1\2", line)
    line = re.sub(r"\*\*([^*\n]+)\*\*([A-Za-z0-9(])", r"**\1** \2", line)
    line = re.sub(r"([A-Za-z0-9.,)])\*\*([^*\n]+)\*\*", r"\1 **\2**", line)
    line = re.sub(r"([A-Za-z0-9])(\[)", r"\1 \2", line)
    line = re.sub(r"\](\w)", r"] \1", line)
    line = re.sub(r"([.?!:;])([A-Z])", r"\1 \2", line)
    line = re.sub(r"([.?!:;])(`[^`]+`)", r"\1 \2", line)
    line = re.sub(r"([A-Za-z0-9])(`[^`]+`)", r"\1 \2", line)
    line = re.sub(r"(`[^`]+`)([A-Za-z0-9])", r"\1 \2", line)
    return line.strip()


def clean_join_artifacts(line: str) -> str:
    line = re.sub(r"(`[^`]+`)\s+([,.;:)])", r"\1\2", line)
    line = re.sub(r"([.?!:;])(`[^`]+`)", r"\1 \2", line)
    return line


def should_drop_blank(prev_line: str, next_line: str) -> bool:
    prev = prev_line.strip()
    nxt = next_line.strip()
    if not prev or not nxt or is_block_line(prev) or is_block_line(nxt):
        return False
    if prev.endswith(("(", "[", "{", "/", ":", ";", ",")):
        return True
    if re.search(
        r"\b(a|an|and|are|as|at|be|between|by|for|from|has|have|if|in|is|of|on|or|that|the|their|this|to|was|were|with)$",
        prev,
    ):
        return True
    if nxt.startswith(("`", "**", "*", "(", ")", "[", ".", ",", ":", ";")):
        return True
    if re.match(r"^[a-z]", nxt):
        return True
    return False


def join_markdown_lines(lines: list[str]) -> list[str]:
    joined: list[str] = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            joined.append(line)
            continue

        if in_code_block or not joined:
            joined.append(line)
            continue

        if stripped in {".", ",", ":", ";", "!", "?"}:
            joined[-1] = joined[-1].rstrip() + stripped
            continue

        previous = joined[-1]
        previous_stripped = previous.strip()
        if (
            previous_stripped
            and stripped
            and not is_block_line(previous_stripped)
            and not is_block_line(stripped)
        ):
            joined[-1] = f"{previous.rstrip()} {stripped}"
            continue

        if previous_stripped and is_list_item(previous_stripped) and not is_block_line(stripped):
            joined[-1] = f"{previous.rstrip()} {stripped}"
            continue

        joined.append(line)

    return joined


def clean_markdown(markdown: str) -> str:
    markdown = re.sub(r"(?<!\n)(#{2,6}\s)", r"\n\n\1", markdown)
    markdown = re.sub(r"([.!?])\s+(-\s)", r"\1\n\2", markdown)
    cleaned: list[str] = []
    blank_run = 0

    for raw_line in markdown.splitlines():
        line = fix_inline_spacing(raw_line.rstrip())
        if not line:
            blank_run += 1
            if blank_run <= 1:
                cleaned.append("")
            continue
        if line.strip() == "#":
            continue

        blank_run = 0
        cleaned.append(line)

    squeezed: list[str] = []
    for index, line in enumerate(cleaned):
        if line != "":
            squeezed.append(line)
            continue

        prev_line = next((item for item in reversed(squeezed) if item != ""), "")
        next_line = next((item for item in cleaned[index + 1 :] if item != ""), "")
        if should_drop_blank(prev_line, next_line):
            continue
        if squeezed and squeezed[-1] != "":
            squeezed.append("")

    cleaned = [clean_join_artifacts(line) if line else "" for line in join_markdown_lines(squeezed)]
    return "\n".join(cleaned).strip()


def extract_markdown(html: str, url: str) -> str | None:
    markdown = trafilatura.extract(
        html,
        url=url,
        output_format="markdown",
        include_tables=True,
        include_links=False,
        include_formatting=True,
        favor_precision=True,
    )
    if markdown:
        markdown = clean_markdown(markdown)
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

            markdown = extract_markdown(html, url)
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
