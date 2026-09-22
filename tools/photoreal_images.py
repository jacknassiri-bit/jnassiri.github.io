#!/usr/bin/env python3
"""Build committed JPG heroes, thumbnail crops, diagrams, and social cards.

Photo masters come from one-time image-generation output placed in
tools/out/photo-sources. Existing committed heroes are reused when those source
files are absent. This script never calls an image-generation service.
"""
from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ITEMS = json.loads((Path(__file__).with_name("images.spec.json")).read_text())
SOURCE_DIR = ROOT / "tools" / "out" / "photo-sources"

DIAGRAMS = {
    "fda-testing-generative-medical-ai",
    "medical-chatbots-danger",
    "ai-replacing-radiologists",
    "ai-drug-discovery",
    "llms-clinic",
    "smart-implants",
}

ALTS = {
    "medical-ai-real-world": "AI generated illustration of a hospital workstation at night with a clinician typing at a keyboard",
    "ai-liver-cancer-second-reader": "AI generated illustration of a radiologist reviewing a blurred grayscale display in a reading room",
    "fda-testing-generative-medical-ai": "Diagram showing nonclinical testing, clinical confirmation, and postmarket monitoring",
    "ai-designed-drug-rentosertib": "AI generated illustration of gloved hands using a pipette above unlabeled laboratory vials",
    "ai-mammography-autonomous": "AI generated illustration of a technologist adjusting a mammography machine in an empty imaging suite",
    "beta-alanine-endurance": "AI generated illustration of a cyclist training on an outdoor track",
    "ai-sepsis-alerts": "AI generated illustration of a nurse walking through a hospital ward corridor at night",
    "testosterone-muscle": "AI generated illustration of a lifter chalking their hands beside a gym weight rack",
    "ai-heart-attack-prediction": "AI generated illustration of a patient using a retinal imaging device in a clinic",
    "sarms-risk": "AI generated illustration of unlabeled capsules beside an open shipping box",
    "ai-cancer-screening": "AI generated illustration of a two monitor radiology reading station",
    "protein-timing": "AI generated illustration of a gym bag, shaker bottle, and banana on a locker room bench",
    "medical-chatbots-danger": "Diagram showing the gap between a patient message and the clinical information a clinician can review",
    "ai-replacing-radiologists": "Diagram comparing software tasks with the work a radiologist still handles",
    "caffeine-performance": "AI generated illustration of coffee, running shoes, and a training notebook on a kitchen table",
    "sleep-testosterone": "AI generated illustration of a dim bedroom with a phone face down on the nightstand",
    "ozempic-muscle-loss": "AI generated illustration of a balanced meal beside a resistance band in a kitchen",
    "bpc157-peptides": "AI generated illustration of an unlabeled vial and capped syringe on a clinical tray",
    "supplements-evidence": "AI generated illustration of blank supplement containers arranged on a shelf",
    "protein-muscle-growth": "AI generated illustration of eggs, chicken, greens, and a shaker bottle on a kitchen table",
    "hgh-muscle-growth": "AI generated illustration of an empty consultation room with a blurred chart on a tablet",
    "ai-hospital-triage": "AI generated illustration of a nurse working at an emergency department triage desk",
    "creatine-guide": "AI generated illustration of a scoop of white powder above an unlabeled container near a gym bag",
    "ambient-ai-scribes": "AI generated illustration of a doctor and patient talking with a small recording device on the desk",
    "carbs-training": "AI generated illustration of a bowl of pasta beside a gym bag in a home kitchen",
    "lean-bulk": "AI generated illustration of a hand portioning rice onto a plate resting on a kitchen scale",
    "sleep-muscle-growth": "AI generated illustration of a quiet bedroom with a folded training shirt on a chair",
    "robotic-surgery": "AI generated illustration of an unoccupied surgical robot in an operating room",
    "ai-drug-discovery": "Diagram showing where current AI evidence sits in the drug development pipeline",
    "wearable-biosensors": "AI generated illustration of an unbranded smartwatch displaying an abstract pulse line outdoors",
    "llms-clinic": "Diagram comparing what a language model drafts with what a clinician decides",
    "crispr-2026": "AI generated illustration of gloved hands using a multichannel pipette over a sequencing plate",
    "ai-pathology": "AI generated illustration of a pathologist viewing a blurred generic tissue image",
    "smart-implants": "Diagram showing an implant alert moving through a home device and clinic queue to a clinician",
    "next-gen-imaging": "AI generated illustration of an empty modern CT scanner suite",
    "ai-mental-health": "AI generated illustration of a quiet telehealth desk with a blurred generic video call on a laptop",
}

CATEGORY = {
    "AI": ("AI IN MEDICINE", "#2563a8", "#7dd3fc"),
    "ANA": ("ANABOLICS", "#7c3aed", "#c4b5fd"),
    "MT": ("MED TECH", "#475569", "#cbd5e1"),
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    options = ([
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ] if bold else [
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ])
    for option in options:
        if Path(option).exists():
            return ImageFont.truetype(option, size)
    return ImageFont.load_default(size=size)


def display_font(size: int) -> ImageFont.FreeTypeFont:
    for option in (
        "/System/Library/Fonts/NewYork.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
    ):
        if Path(option).exists():
            return ImageFont.truetype(option, size)
    return font(size, bold=True)


def save_jpeg(im: Image.Image, path: Path, max_bytes: int, start_quality: int = 84) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im = im.convert("RGB")
    for quality in range(start_quality, 47, -3):
        im.save(path, "JPEG", quality=quality, optimize=True, progressive=True, subsampling=2)
        if path.stat().st_size <= max_bytes:
            return
    raise RuntimeError(f"Could not compress {path.relative_to(ROOT)} below {max_bytes} bytes")


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str, width: int = 9) -> None:
    draw.line((start, end), fill=color, width=width)
    x, y = end
    draw.polygon(((x, y), (x - 24, y - 16), (x - 24, y + 16)), fill=color)


def label_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, body: list[str], accent: str) -> None:
    draw.rounded_rectangle(box, radius=24, fill="#16233b", outline=accent, width=4)
    x1, y1, x2, y2 = box
    draw.text((x1 + 30, y1 + 28), title, font=font(26, bold=True), fill="#ffffff")
    y = y1 + 82
    for line in body:
        draw.ellipse((x1 + 30, y + 7, x1 + 41, y + 18), fill=accent)
        draw.text((x1 + 58, y), line, font=font(23), fill="#dbeafe")
        y += 48


def diagram(slug: str, category: str) -> Image.Image:
    _, base_accent, pale = CATEGORY[category]
    im = Image.new("RGB", (1600, 900), "#0c1a3a")
    draw = ImageDraw.Draw(im)
    draw.ellipse((1080, -180, 1700, 430), fill="#13284d")
    draw.ellipse((-260, 610, 460, 1270), fill="#111f39")

    if slug == "fda-testing-generative-medical-ai":
        titles = ["NONCLINICAL BENCHMARK", "CLINICAL CONFIRMATION", "POSTMARKET MONITORING"]
        bodies = [["Test before release"], ["Confirm in practice"], ["Keep checking updates"]]
        xs = [100, 590, 1080]
        for x, title, body in zip(xs, titles, bodies):
            label_box(draw, (x, 280, x + 390, 570), title, body, pale)
        arrow(draw, (500, 425), (570, 425), pale)
        arrow(draw, (990, 425), (1060, 425), pale)
    elif slug == "medical-chatbots-danger":
        label_box(draw, (90, 220, 570, 650), "PATIENT MESSAGE", ["Typed symptoms", "One moment in time"], pale)
        label_box(draw, (1030, 220, 1510, 650), "CLINICIAN VIEW", ["Chart and exam", "Allergies and medication", "A follow up question"], pale)
        draw.line((610, 435, 735, 435), fill=pale, width=9)
        draw.line((865, 435, 990, 435), fill=pale, width=9)
        draw.text((686, 335), "MISSING", font=font(24, bold=True), fill="#fbbf24")
        draw.text((667, 472), "CLINICAL CONTEXT", font=font(21, bold=True), fill="#fbbf24")
    elif slug == "ai-replacing-radiologists":
        label_box(draw, (120, 145, 740, 755), "SOFTWARE HANDLES", ["Flags an urgent scan", "Prioritizes the worklist", "Finds a narrow pattern", "Drafts a first pass"], pale)
        label_box(draw, (860, 145, 1480, 755), "RADIOLOGIST HANDLES", ["Compares prior images", "Uses clinical history", "Decides what changes care", "Owns the final report"], pale)
    elif slug == "ai-drug-discovery":
        labels = ["TARGET", "MOLECULE", "PRECLINICAL", "PHASE 1", "PHASE 2", "PHASE 3", "APPROVAL"]
        x = 80
        for index, value in enumerate(labels):
            width = 185 if index < 2 else 174
            color = "#38bdf8" if index < 2 else "#64748b"
            draw.rounded_rectangle((x, 350, x + width, 510), 22, fill="#16233b", outline=color, width=5)
            bbox = draw.textbbox((0, 0), value, font=font(23, bold=True))
            draw.text((x + (width - (bbox[2] - bbox[0])) / 2, 413), value, font=font(23, bold=True), fill="#ffffff")
            if index < len(labels) - 1:
                arrow(draw, (x + width + 10, 430), (x + width + 34, 430), pale, width=5)
            x += width + 42
        draw.text((100, 270), "AI EVIDENCE SO FAR", font=font(26, bold=True), fill="#7dd3fc")
        draw.text((600, 270), "STILL AHEAD", font=font(26, bold=True), fill="#cbd5e1")
    elif slug == "llms-clinic":
        label_box(draw, (120, 145, 740, 755), "THE MODEL DRAFTS", ["Retrieves a guideline", "Organizes the chart", "Suggests questions", "Drafts a note"], pale)
        label_box(draw, (860, 145, 1480, 755), "THE CLINICIAN DECIDES", ["Final diagnosis", "Medication doses", "Treatment choice", "Patient explanation"], pale)
    elif slug == "smart-implants":
        labels = ["IMPLANT", "HOME HUB OR PHONE", "CLINIC QUEUE", "CLINICIAN ACTION"]
        ys = [80, 270, 500, 710]
        for index, (value, y) in enumerate(zip(labels, ys)):
            color = "#e2e8f0" if index != 2 else "#fbbf24"
            draw.rounded_rectangle((460, y, 1140, y + 115), 24, fill="#16233b", outline=color, width=5)
            bbox = draw.textbbox((0, 0), value, font=font(29, bold=True))
            draw.text((800 - (bbox[2] - bbox[0]) / 2, y + 39), value, font=font(29, bold=True), fill="#ffffff")
            if index < 3:
                draw.line((800, y + 116, 800, y + 170), fill=pale, width=8)
                draw.polygon(((800, y + 185), (784, y + 160), (816, y + 160)), fill=pale)
        draw.text((1180, 532), "ALERT CAN WAIT HERE", font=font(22, bold=True), fill="#fbbf24")
        draw.line((1150, 558, 1122, 558), fill="#fbbf24", width=5)
    else:
        raise ValueError(f"Unknown diagram slug: {slug}")
    return im


def prepare_hero(item: dict) -> Image.Image:
    slug = item["slug"]
    hero_path = ROOT / "images" / "heroes" / f"{slug}.jpg"
    source_path = SOURCE_DIR / f"{slug}.png"
    if slug in DIAGRAMS:
        return diagram(slug, item["category"])
    if source_path.exists():
        source = Image.open(source_path).convert("RGB")
        return ImageOps.fit(source, (1600, 900), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    if hero_path.exists():
        return Image.open(hero_path).convert("RGB")
    raise FileNotFoundError(f"Missing one-time photo source for {slug}: {source_path}")


def wrap_title(draw: ImageDraw.ImageDraw, title: str, chosen_font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in title.split():
        trial = f"{current} {word}".strip()
        if current and draw.textlength(trial, font=chosen_font) > width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def og_card(item: dict, hero: Image.Image) -> Image.Image:
    background = ImageOps.fit(hero, (1200, 630), Image.Resampling.LANCZOS).convert("RGBA")
    overlay = Image.new("RGBA", background.size)
    pixels = overlay.load()
    for x in range(1200):
        alpha = int(220 - 90 * (x / 1199))
        for y in range(630):
            pixels[x, y] = (5, 12, 25, alpha)
    background.alpha_composite(overlay)
    draw = ImageDraw.Draw(background)
    chip, base_accent, pale = CATEGORY[item["category"]]
    draw.rounded_rectangle((62, 48, 330, 96), radius=24, fill=base_accent)
    draw.text((84, 60), chip, font=font(22, bold=True), fill="#ffffff")

    title_font = display_font(54)
    lines = wrap_title(draw, item["title"], title_font, 690)
    if len(lines) > 3:
        title_font = display_font(48)
        lines = wrap_title(draw, item["title"], title_font, 700)
    if len(lines) > 3:
        title_font = display_font(43)
        lines = wrap_title(draw, item["title"], title_font, 710)
    y = 142
    spacing = int(title_font.size * 1.18)
    for line in lines[:3]:
        draw.text((62, y), line, font=title_font, fill="#ffffff", stroke_width=1, stroke_fill="#08111f")
        y += spacing
    draw.text((62, 550), "The Med", font=display_font(28), fill="#ffffff")
    x = 62 + draw.textlength("The Med ", font=display_font(28))
    draw.text((x, 550), "Frontier", font=display_font(28), fill=pale)
    return background.convert("RGB")


def contact_sheet(items: list[dict]) -> None:
    cols, tile_w, tile_h = 6, 300, 178
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile_w, rows * tile_h + 58), "#eef2f7")
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 15), "The Med Frontier: photographic heroes and diagrams", font=font(27, bold=True), fill="#0f172a")
    for index, item in enumerate(items):
        col, row = index % cols, index // cols
        x, y = col * tile_w, 58 + row * tile_h
        thumb = Image.open(ROOT / "images" / "thumbs" / f'{item["slug"]}.jpg').convert("RGB")
        thumb = thumb.resize((288, 96), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x + 6, y + 6))
        label = textwrap.wrap(item["slug"], width=32)[:2]
        draw.multiline_text((x + 8, y + 110), "\n".join(label), font=font(16, bold=True), fill="#0f172a", spacing=3)
        draw.text((x + 8, y + 151), "Diagram" if item["slug"] in DIAGRAMS else "Photo", font=font(14), fill="#475569")
    output = ROOT / "tools" / "out" / "photoreal-contact-sheet.jpg"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, "JPEG", quality=88, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", action="append", help="Build one slug. May be repeated.")
    args = parser.parse_args()
    selected = [item for item in ITEMS if not args.only or item["slug"] in set(args.only)]
    for item in selected:
        slug = item["slug"]
        hero = prepare_hero(item)
        hero_path = ROOT / "images" / "heroes" / f"{slug}.jpg"
        save_jpeg(hero, hero_path, 300 * 1024, start_quality=84)
        committed_hero = Image.open(hero_path).convert("RGB")
        thumb = ImageOps.fit(committed_hero, (900, 300), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        save_jpeg(thumb, ROOT / "images" / "thumbs" / f"{slug}.jpg", 80 * 1024, start_quality=82)
        save_jpeg(og_card(item, committed_hero), ROOT / "images" / "og" / f"{slug}.jpg", 200 * 1024, start_quality=82)
    if not args.only:
        contact_sheet(ITEMS)
    print(f"Built {len(selected)} photographic image sets ({sum(1 for x in selected if x['slug'] in DIAGRAMS)} diagrams).")


if __name__ == "__main__":
    main()
