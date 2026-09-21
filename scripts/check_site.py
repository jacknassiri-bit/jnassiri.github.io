#!/usr/bin/env python3
"""Validate The Med Frontier static site with Python's standard library only."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://themedfrontier.com"
OLD_BASE = "/".join(("https://jacknassiri-bit.github.io", "jnassiri.github.io"))
EXCLUDED_HTML = {"post-template.html", "liberation-wars.html", "med-tech.html"}
LIVE_HTML = sorted(path for path in ROOT.glob("*.html") if path.name not in EXCLUDED_HTML)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.images: list[dict[str, str | None]] = []
        self.canonical: str | None = None
        self.description: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if data.get("id"):
            self.ids.add(data["id"] or "")
        if tag == "a":
            if data.get("name"):
                self.ids.add(data["name"] or "")
            if data.get("href"):
                self.links.append(data["href"] or "")
        elif tag == "img":
            self.images.append(data)
        elif tag == "link" and (data.get("rel") or "").lower() == "canonical":
            self.canonical = data.get("href")
        elif tag == "meta" and (data.get("name") or "").lower() == "description":
            self.description = data.get("content")


def parse_page(path: Path) -> tuple[str, PageParser]:
    text = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(text)
    return text, parser


def site_path(source: Path, raw_path: str) -> Path:
    decoded = unquote(raw_path)
    if decoded.startswith("/"):
        decoded = decoded.lstrip("/")
        if decoded.startswith("jnassiri.github.io/"):
            decoded = decoded.removeprefix("jnassiri.github.io/")
        return ROOT / (decoded or "index.html")
    return (source.parent / (decoded or source.name)).resolve()


def main() -> int:
    errors: list[str] = []
    parsed: dict[Path, tuple[str, PageParser]] = {path: parse_page(path) for path in LIVE_HTML}

    old_url_hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if OLD_BASE in text:
            old_url_hits.append(str(path.relative_to(ROOT)))
    if old_url_hits:
        errors.append("Old GitHub Pages URL remains in: " + ", ".join(old_url_hits))

    for path, (_text, page) in parsed.items():
        if not page.canonical:
            errors.append(f"{path.name}: missing canonical link")
        if not (page.description or "").strip():
            errors.append(f"{path.name}: missing meta description")
        for index, image in enumerate(page.images, start=1):
            classes = (image.get("class") or "").split()
            decorative_hero = "hero-img" in classes and image.get("alt") == ""
            if image.get("alt") is None or (not (image.get("alt") or "").strip() and not decorative_hero):
                errors.append(f"{path.name}: image {index} has missing or empty alt text")

    parser_cache: dict[Path, PageParser] = {path.resolve(): data[1] for path, data in parsed.items()}
    for source, (_text, page) in parsed.items():
        for href in page.links:
            parts = urlsplit(href)
            if parts.scheme in {"http", "https", "mailto", "tel", "javascript"} or href.startswith("//"):
                continue
            target = site_path(source, parts.path)
            if not target.exists():
                errors.append(f"{source.name}: broken internal link {href}")
                continue
            if parts.fragment and target.suffix.lower() == ".html":
                target_parser = parser_cache.get(target.resolve())
                if target_parser is None:
                    try:
                        target_parser = parse_page(target)[1]
                    except (OSError, UnicodeDecodeError):
                        continue
                    parser_cache[target.resolve()] = target_parser
                if unquote(parts.fragment) not in target_parser.ids:
                    errors.append(f"{source.name}: missing anchor #{parts.fragment} in {target.name}")

    sitemap_path = ROOT / "sitemap.xml"
    try:
        sitemap_root = ElementTree.parse(sitemap_path).getroot()
        sitemap_urls = {node.text for node in sitemap_root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
    except (OSError, ElementTree.ParseError) as exc:
        errors.append(f"sitemap.xml: cannot parse ({exc})")
        sitemap_urls = set()

    articles: list[tuple[Path, dict[str, object]]] = []
    schema_pattern = re.compile(r'<script type="application/ld\+json" data-site-schema>(.*?)</script>', re.S)
    for path, (text, _page) in parsed.items():
        for match in schema_pattern.finditer(text):
            try:
                schema = json.loads(match.group(1))
            except json.JSONDecodeError as exc:
                errors.append(f"{path.name}: invalid JSON-LD ({exc})")
                continue
            if schema.get("@type") == "Article":
                articles.append((path, schema))
                expected = f"{BASE}/{path.name}"
                if expected not in sitemap_urls:
                    errors.append(f"{path.name}: article missing from sitemap.xml")

    home_text = (ROOT / "index.html").read_text(encoding="utf-8")
    card_pattern = re.compile(r'<a\b[^>]*href="([^"]+\.html)"[^>]*class="post-card"[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*>', re.S)
    cards = [(href, date) for href, date in card_pattern.findall(home_text)]
    if not cards:
        errors.append("index.html: no dated homepage article cards found")
    else:
        newest_href = max(cards, key=lambda item: item[1])[0]
        hero_href = re.search(r'<a href="([^"]+)" class="hero-btn">Read the latest', home_text)
        featured_href = re.search(r'<a class="featured-card" href="([^"]+)">', home_text)
        if not hero_href or hero_href.group(1) != newest_href:
            errors.append(f"index.html: Read the latest does not match newest card ({newest_href})")
        if not featured_href or featured_href.group(1) != newest_href:
            errors.append(f"index.html: Latest post card does not match newest card ({newest_href})")

    if errors:
        print(f"FAIL: {len(errors)} site check error(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS: {len(LIVE_HTML)} live HTML pages checked")
    print(f"PASS: {len(articles)} article pages are present in sitemap.xml")
    print("PASS: canonical URLs, descriptions, image alternatives, internal links, and anchors")
    print("PASS: homepage latest-post links match the newest dated article card")
    print("PASS: no legacy GitHub Pages URLs remain")
    return 0


if __name__ == "__main__":
    sys.exit(main())
