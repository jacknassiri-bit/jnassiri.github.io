#!/usr/bin/env python3
"""Apply generated image paths and figure snippets to the static HTML."""
from __future__ import annotations

import argparse
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


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--art",action="store_true"); ap.add_argument("--figures",type=int,choices=(1,2))
    a=ap.parse_args()
    if a.art: apply_art()
    if a.figures: apply_figures(a.figures)


if __name__ == "__main__": main()
