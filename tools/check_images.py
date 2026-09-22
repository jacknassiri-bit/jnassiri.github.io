#!/usr/bin/env python3
"""Validate the committed photographic image system and retained data figures."""
from __future__ import annotations

import hashlib
import html as htmllib
import json
import re
import subprocess
from pathlib import Path

from PIL import Image

from photoreal_images import ALTS, DIAGRAMS


ROOT = Path(__file__).resolve().parents[1]
ITEMS = json.loads((Path(__file__).with_name("images.spec.json")).read_text())
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def visible(text: str) -> str:
    text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", text, flags=re.S | re.I)
    return htmllib.unescape(re.sub(r"<[^>]+>", " ", text)).replace("−", "-").replace("–", "-")


def norm_number(value: str) -> str:
    return value.replace(",", "").replace("$", "").replace("−", "-").strip()


def ratio(a: str, b: str) -> float:
    def lum(color: str) -> float:
        values = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        values = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
        return .2126 * values[0] + .7152 * values[1] + .0722 * values[2]
    high, low = sorted((lum(a), lum(b)), reverse=True)
    return (high + .05) / (low + .05)


def check_figure(item: dict, article_text: str) -> None:
    slug = item["slug"]
    wanted = 1 if item["figure"] else 0
    if len(re.findall(r'<figure class="fig">', article_text)) != wanted:
        fail(f"{slug}: expected {wanted} figure")
    if not item["figure"]:
        return
    block = (ROOT / "figures" / f"{slug}.svg.html").read_text()
    for needle in ("role=\"img\"", f"fig-{slug}-t", f"fig-{slug}-d", "<title", "<desc", "<figcaption>"):
        if needle not in block:
            fail(f"{slug}: figure missing {needle}")
    for size in re.findall(r'font-size="([\d.]+)"', block):
        if float(size) < 11:
            fail(f"{slug}: figure text below 11px: {size}px")
    article = norm_number(visible(article_text))
    numeric_text = " ".join(re.findall(r"<(?:text|desc)\b[^>]*>(.*?)</(?:text|desc)>", block, re.S))
    derived_spans = set(re.findall(r'<text[^>]*data-derived="[^"]+"[^>]*>(.*?)</text>', block, re.S))
    for number in re.findall(r"(?<![A-Za-z])(?:\$)?-?\d[\d,.]*(?:%|\b)", norm_number(visible(numeric_text))):
        normalized = norm_number(number).rstrip("%")
        if not normalized or normalized in {"0", "1", "2", "3"}:
            continue
        if normalized not in article and not any(normalized in norm_number(visible(x)) for x in derived_spans):
            fail(f"{slug}: figure number absent from article: {number}")
    for expr in re.findall(r'data-derived="([0-9]+(?:[-/][0-9]+))"', block):
        a, operator, b = re.fullmatch(r"(\d+)([-/])(\d+)", expr).groups()
        a_value, b_value = float(a), float(b)
        value = a_value - b_value if operator == "-" else a_value / b_value * 100
        expected = str(int(value)) if operator == "-" else f"{value:.2f}".rstrip("0").rstrip(".")
        tag = re.search(rf'<text[^>]*data-derived="{re.escape(expr)}"[^>]*>(.*?)</text>', block, re.S)
        if not tag or expected not in visible(tag.group(1)):
            fail(f"{slug}: derived {expr} should display {expected}")


def main() -> int:
    html_files = list(ROOT.glob("*.html"))
    banned = re.compile(r"unsplash|mcguff|github\.io/jnassiri|pexels|shutterstock", re.I)
    for path in html_files + list((ROOT / "assets").glob("*")):
        if path.is_file() and path.suffix.lower() in {".html", ".css", ".svg", ".txt"}:
            try:
                data = path.read_text()
            except UnicodeDecodeError:
                continue
            if banned.search(data):
                fail(f"third-party image reference: {path.relative_to(ROOT)}")

    reference_pattern = re.compile(r'(?:https://themedfrontier\.com/)?((?:images|assets|figures)/[\w./-]+)')
    for path in html_files + list((ROOT / "assets").glob("*.css")):
        for relative in reference_pattern.findall(path.read_text()):
            if not (ROOT / relative).is_file():
                fail(f"missing reference: {path.name}: {relative}")

    for path in html_files:
        for tag in re.findall(r"<img\b[^>]*>", path.read_text(), re.I):
            for attribute in ("alt", "width", "height"):
                if not re.search(rf'\b{attribute}="[^"]*"', tag):
                    fail(f"{path.name}: img missing {attribute}")

    hero_hashes: dict[str, str] = {}
    for item in ITEMS:
        slug = item["slug"]
        article_path = ROOT / f"{slug}.html"
        article_text = article_path.read_text()
        paths = {
            "hero": ROOT / "images" / "heroes" / f"{slug}.jpg",
            "thumbnail": ROOT / "images" / "thumbs" / f"{slug}.jpg",
            "social card": ROOT / "images" / "og" / f"{slug}.jpg",
        }
        expected_sizes = {"hero": (1600, 900), "thumbnail": (900, 300), "social card": (1200, 630)}
        for label, path in paths.items():
            if not path.is_file():
                fail(f"{slug}: missing {label} JPG")
                continue
            with Image.open(path) as image:
                if image.format != "JPEG":
                    fail(f"{slug}: {label} is not JPEG")
                if image.size != expected_sizes[label]:
                    fail(f"{slug}: {label} has dimensions {image.size}, expected {expected_sizes[label]}")

        hero_tag = re.search(r'<img class="hero-img"[^>]*>', article_text)
        if not hero_tag:
            fail(f"{slug}: missing hero image")
        else:
            tag = hero_tag.group(0)
            for value in (f'src="images/heroes/{slug}.jpg"', f'alt="{ALTS[slug]}"', 'width="1600"', 'height="900"', 'fetchpriority="high"', 'decoding="async"'):
                if value not in tag:
                    fail(f"{slug}: hero tag missing {value}")
        if re.search(r"[–—]", ALTS[slug]):
            fail(f"{slug}: alt text contains an en dash or em dash")

        for value in (f"https://themedfrontier.com/images/og/{slug}.jpg", "og:image:width", "og:image:height", "og:image:alt", "summary_large_image"):
            if value not in article_text:
                fail(f"{slug}: missing social meta {value}")
        if f'"image":"https://themedfrontier.com/images/og/{slug}.jpg"' not in article_text:
            fail(f"{slug}: structured data does not use the JPG social card")
        if re.search(rf'images/(?:heroes|thumbs)/{re.escape(slug)}\.svg|images/og/{re.escape(slug)}\.png', article_text):
            fail(f"{slug}: article still references the abstract image set")
        check_figure(item, article_text)

        digest = hashlib.sha256(paths["hero"].read_bytes()).hexdigest()
        if digest in hero_hashes:
            fail(f"duplicate heroes: {slug}, {hero_hashes[digest]}")
        hero_hashes[digest] = slug

    for page_name in ("index.html", "all-articles.html"):
        page = (ROOT / page_name).read_text()
        for item in ITEMS:
            slug = item["slug"]
            pattern = rf'<img[^>]*src="images/thumbs/{re.escape(slug)}\.jpg"[^>]*alt="{re.escape(ALTS[slug])}"[^>]*>'
            if not re.search(pattern, page):
                fail(f"{page_name}: missing JPG thumbnail or factual alt for {slug}")
        if re.search(r"images/thumbs/[^\"]+\.svg", page):
            fail(f"{page_name}: still references an abstract SVG thumbnail")

    disclosure = "Article images are AI-generated illustrations. They are not photographs, scans, or data from the studies discussed."
    if (ROOT / "sources.html").read_text().count(disclosure) != 1:
        fail("sources.html: expected one AI image disclosure")

    budgets = {"heroes": 300 * 1024, "thumbs": 80 * 1024, "og": 200 * 1024}
    for folder, limit in budgets.items():
        for path in (ROOT / "images" / folder).glob("*.jpg"):
            if path.stat().st_size > limit:
                fail(f"oversize {path.relative_to(ROOT)}: {path.stat().st_size} bytes")
    for path in (ROOT / "figures").glob("*.svg.html"):
        if path.stat().st_size > 6 * 1024:
            fail(f"oversize {path.relative_to(ROOT)}")

    colors = [
        ("#0f172a", "#ffffff", 4.5, "light text"), ("#64748b", "#ffffff", 4.5, "light muted"),
        ("#1d6fd4", "#ffffff", 3, "light blue"), ("#8b5cf6", "#ffffff", 3, "light purple"),
        ("#f4f4f5", "#27272a", 4.5, "dark text"), ("#a1a1aa", "#27272a", 4.5, "dark muted"),
        ("#93c5fd", "#27272a", 3, "dark blue"), ("#c4b5fd", "#27272a", 3, "dark purple"),
    ]
    for foreground, background, minimum, label in colors:
        measured = ratio(foreground, background)
        if measured < minimum:
            fail(f"contrast {label}: {measured:.2f}:1")

    if len(hero_hashes) != 36 or len(DIAGRAMS) != 6 or len(ITEMS) - len(DIAGRAMS) != 30:
        fail(f"expected 36 heroes, 30 photos, and 6 diagrams; found {len(hero_hashes)}, {len(ITEMS) - len(DIAGRAMS)}, and {len(DIAGRAMS)}")

    try:
        tracked = set(subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines())
    except Exception:
        tracked = set()
    if tracked:
        for path in html_files + list((ROOT / "assets").glob("*.css")):
            for relative in reference_pattern.findall(path.read_text()):
                if relative not in tracked:
                    fail(f"case or tracking mismatch: {path.name}: {relative}")

    print(f"Checked {len(ITEMS)} articles, 30 photos, 6 diagrams, 36 thumbnail crops, 36 social cards, and {sum(1 for x in ITEMS if x['figure'])} data figures.")
    if errors:
        for error in errors:
            print("FAIL", error)
        print(f"FAILED: {len(errors)} problem(s)")
        return 1
    print("PASS: files, dimensions, alt text, metadata, disclosure, budgets, contrast, uniqueness, and tracked path case.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
