#!/usr/bin/env python3
"""Apply generated image paths and figure snippets to the static HTML."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEMS = json.loads((Path(__file__).with_name("images.spec.json")).read_text())


def write_if_changed(path: Path, text: str) -> None:
    if path.read_text() != text:
        path.write_text(text)


def apply_art() -> None:
    for item in ITEMS:
        slug=item["slug"]; path=ROOT/f"{slug}.html"; text=path.read_text()
        hero=(f'<figure class="article-visual"><img class="hero-img" src="images/heroes/{slug}.svg" '
              f'alt="" width="1600" height="420" fetchpriority="high" decoding="async"></figure>')
        text,n=re.subn(r'<figure class="article-visual"><img\b.*?</figure>',hero,text,count=1,flags=re.S)
        if not n:
            text,n=re.subn(r'<div class="article-visual" aria-hidden="true"></div>',hero,text,count=1)
        if n != 1: raise SystemExit(f"hero markup not found once: {path.name}")
        write_if_changed(path,text)
    for name in ("index.html","all-articles.html"):
        path=ROOT/name; text=path.read_text()
        for item in ITEMS:
            slug=item["slug"]
            pattern=(rf'src="images/{re.escape(slug)}-1600\.webp"\s+'
                     rf'srcset="images/{re.escape(slug)}-800\.webp 800w, images/{re.escape(slug)}-1200\.webp 1200w, images/{re.escape(slug)}-1600\.webp 1600w"\s+'
                     rf'sizes="100vw"\s+width="1600"\s+height="900"')
            text=re.sub(pattern,f'src="images/thumbs/{slug}.svg" width="900" height="300"',text)
        write_if_changed(path,text)


def insert_after_section(text: str, heading: str, snippet: str) -> tuple[str,bool]:
    marker=f'<h2>{heading}</h2>'; start=text.find(marker)
    if start < 0: return text,False
    end=text.find('<h2>',start+len(marker))
    if end < 0:
        candidates=[p for p in (text.find('<div class="share',start),text.find('<section class="refs',start),text.find('<div class="citations',start)) if p>=0]
        end=min(candidates) if candidates else len(text)
    return text[:end].rstrip()+"\n\n"+snippet+"\n\n"+text[end:],True


def apply_figures(tier: int) -> None:
    anchors={
      "medical-ai-real-world":("before-heading","Workflow is part of the medical intervention"),
      "ai-liver-cancer-second-reader":("end","What the system caught"),
      "ai-designed-drug-rentosertib":("end","What the phase 2a trial found"),
      "ai-mammography-autonomous":("end","The workload result was hard to ignore"),
      "beta-alanine-endurance":("end","The newer review found a small effect"),
      "ai-sepsis-alerts":("end","Randomized trials make the question more real"),
      "sarms-risk":("end","The supplement label is misleading"),
      "ai-cancer-screening":("end","Mammography is leading the way"),
      "caffeine-performance":("end","The sleep tradeoff"),
      "protein-muscle-growth":("end","Start with the daily total"),
      "hgh-muscle-growth":("end","Lean mass can be a misleading number"),
      "robotic-surgery":("after-paragraph","2 million dollars"),
      "crispr-2026":("after-paragraph","In December 2023, the FDA approved Casgevy"),
      "next-gen-imaging":("after-paragraph","237 of 240"),
      "llms-clinic":("after-first","The assignment changes the risk"),
      "ai-replacing-radiologists":("end","AI is already changing the workflow"),
      "medical-chatbots-danger":("end","The missing detail problem"),
      "ai-heart-attack-prediction":("end","Catch the risk while there is still time"),
      "smart-implants":("after-paragraph","up to two weeks before symptoms became severe"),
      "ai-drug-discovery":("after-paragraph","So far, the strongest case for AI"),
    }
    for item in ITEMS:
        if not item["figure"] or item["figure"]["tier"] != tier: continue
        slug=item["slug"]; path=ROOT/f"{slug}.html"; text=path.read_text(); snippet=(ROOT/"figures"/f"{slug}.svg.html").read_text().strip()
        if f'id="fig-{slug}-t"' in text: continue
        mode,anchor=anchors[slug]; ok=False
        if mode=="before-heading":
            marker=f'<h2>{anchor}</h2>'; pos=text.find(marker)
            if pos>=0: text=text[:pos]+snippet+"\n\n"+text[pos:]; ok=True
        elif mode=="end": text,ok=insert_after_section(text,anchor,snippet)
        elif mode=="after-first":
            marker=f'<h2>{anchor}</h2>'; pos=text.find(marker)
            if pos>=0:
                pend=text.find('</p>',pos)
                if pend>=0: text=text[:pend+4]+"\n\n"+snippet+text[pend+4:]; ok=True
        else:
            pos=text.find(anchor)
            if pos>=0:
                pstart=text.rfind('<p',0,pos); pend=text.find('</p>',pos)
                if pstart>=0 and pend>=0: text=text[:pend+4]+"\n\n"+snippet+text[pend+4:]; ok=True
        if not ok: raise SystemExit(f"figure anchor missing: {slug}: {anchor}")
        write_if_changed(path,text)


def _drop_meta(text: str, key: str, value: str) -> str:
    return re.sub(rf'\s*<meta\s+{key}="{re.escape(value)}"\s+content="[^"]*"\s*/?>', '', text, flags=re.I)


def apply_meta() -> None:
    articles={item["slug"]:item for item in ITEMS}
    for path in sorted(ROOT.glob("*.html")):
        text=path.read_text()
        text=re.sub(r'\s*<link\s+rel="apple-touch-icon"[^>]*>', '', text, flags=re.I)
        text=text.replace('</head>', '<link rel="apple-touch-icon" href="images/icons/apple-touch-icon.png">\n</head>', 1)
        slug=path.stem
        if slug in articles:
            title=articles[slug]["title"]
            for key,value in (("property","og:image"),("property","og:image:width"),("property","og:image:height"),("property","og:image:alt"),("name","twitter:card"),("name","twitter:image")):
                text=_drop_meta(text,key,value)
            block=(f'\n<meta property="og:image" content="https://themedfrontier.com/images/og/{slug}.png">'
                   f'\n<meta property="og:image:width" content="1200">'
                   f'\n<meta property="og:image:height" content="630">'
                   f'\n<meta property="og:image:alt" content="The Med Frontier: {html.escape(title, quote=True)}">'
                   f'\n<meta name="twitter:card" content="summary_large_image">'
                   f'\n<meta name="twitter:image" content="https://themedfrontier.com/images/og/{slug}.png">')
            text=text.replace('</head>',block+'\n</head>',1)
            text=re.sub(r'("image"\s*:\s*")[^"]+("\s*,?\s*"mainEntityOfPage")',rf'\1https://themedfrontier.com/images/og/{slug}.png\2',text)
        elif path.name in {"index.html","all-articles.html","about.html","contact.html","sources.html","search.html","ai-medicine.html","anabolic-nutrition.html","how-i-write.html","med-tech.html","404.html","post-template.html"}:
            for key,value in (("property","og:image"),("name","twitter:image"),("name","twitter:card")):
                text=_drop_meta(text,key,value)
            block=('\n<meta property="og:image" content="https://themedfrontier.com/images/og/default.png">'
                   '\n<meta name="twitter:card" content="summary_large_image">'
                   '\n<meta name="twitter:image" content="https://themedfrontier.com/images/og/default.png">')
            text=text.replace('</head>',block+'\n</head>',1)
        write_if_changed(path,text)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--art",action="store_true"); ap.add_argument("--figures",type=int,choices=(1,2)); ap.add_argument("--meta",action="store_true")
    a=ap.parse_args()
    if a.art: apply_art()
    if a.figures: apply_figures(a.figures)
    if a.meta: apply_meta()


if __name__ == "__main__": main()
