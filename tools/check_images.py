#!/usr/bin/env python3
"""Validate the committed image system. Exits nonzero on any hard failure."""
from __future__ import annotations

import hashlib
import html as htmllib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ITEMS=json.loads((Path(__file__).with_name("images.spec.json")).read_text())
errors=[]; notes=[]


def fail(message): errors.append(message)


def visible(text):
    text=re.sub(r'<script\b.*?</script>|<style\b.*?</style>', ' ', text, flags=re.S|re.I)
    return htmllib.unescape(re.sub(r'<[^>]+>', ' ', text)).replace('−','-').replace('–','-')


def norm_number(s): return s.replace(',','').replace('$','').replace('−','-').strip()


def ratio(a,b):
    def lum(c):
        vals=[int(c[i:i+2],16)/255 for i in (1,3,5)]
        vals=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals]
        return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]
    x,y=sorted((lum(a),lum(b)),reverse=True); return (x+.05)/(y+.05)


def main():
    html_files=list(ROOT.glob('*.html'))
    banned=re.compile(r'unsplash|mcguff|github\.io/jnassiri|pexels|shutterstock',re.I)
    for path in html_files+list((ROOT/'assets').glob('*'))+list((ROOT/'images').rglob('*')):
        if path.is_file() and path.suffix.lower() in {'.html','.css','.svg','.txt'}:
            try: data=path.read_text()
            except UnicodeDecodeError: continue
            if banned.search(data): fail(f'third-party image reference: {path.relative_to(ROOT)}')

    ref_pat=re.compile(r'(?:https://themedfrontier\.com/)?((?:images|assets|figures)/[\w./-]+)')
    for path in html_files+list((ROOT/'assets').glob('*.css')):
        for rel in ref_pat.findall(path.read_text()):
            if not (ROOT/rel).is_file(): fail(f'missing reference: {path.name}: {rel}')

    for path in html_files:
        for tag in re.findall(r'<img\b[^>]*>',path.read_text(),re.I):
            for attr in ('alt','width','height'):
                if not re.search(rf'\b{attr}="[^"]*"',tag): fail(f'{path.name}: img missing {attr}')
            if 'hero-img' in tag and not re.search(r'\balt=""',tag): fail(f'{path.name}: hero alt must be empty')

    for item in ITEMS:
        slug=item['slug']; path=ROOT/f'{slug}.html'; text=path.read_text()
        if len(re.findall(r'class="hero-img"',text)) != 1: fail(f'{slug}: expected one hero')
        for value in (f'https://themedfrontier.com/images/og/{slug}.png','og:image:width','og:image:height','og:image:alt','summary_large_image'):
            if value not in text: fail(f'{slug}: missing social meta {value}')
        wanted=1 if item['figure'] else 0
        if len(re.findall(r'<figure class="fig">',text)) != wanted: fail(f'{slug}: expected {wanted} figure')
        if item['figure']:
            block=(ROOT/'figures'/f'{slug}.svg.html').read_text()
            for needle in ('role="img"',f'fig-{slug}-t',f'fig-{slug}-d','<title','<desc','<figcaption>'):
                if needle not in block: fail(f'{slug}: figure missing {needle}')
            article=norm_number(visible(text))
            numeric_text=' '.join(re.findall(r'<(?:text|desc)\b[^>]*>(.*?)</(?:text|desc)>',block,re.S))
            derived_spans=set(re.findall(r'<text[^>]*data-derived="[^"]+"[^>]*>(.*?)</text>',block,re.S))
            for number in re.findall(r'(?<![A-Za-z])(?:\$)?-?\d[\d,.]*(?:%|\b)',norm_number(visible(numeric_text))):
                n=norm_number(number).rstrip('%')
                if not n or n in {'0','1','2','3'}: continue
                if n not in article and not any(n in norm_number(visible(x)) for x in derived_spans):
                    fail(f'{slug}: figure number absent from article: {number}')
            for expr in re.findall(r'data-derived="([0-9]+(?:[-/][0-9]+))"',block):
                a,op,b=re.fullmatch(r'(\d+)([-/])(\d+)',expr).groups(); a=float(a); b=float(b)
                value=a-b if op=='-' else a/b*100
                expected=str(int(value)) if op=='-' else f'{value:.2f}'.rstrip('0').rstrip('.')
                tag=re.search(rf'<text[^>]*data-derived="{re.escape(expr)}"[^>]*>(.*?)</text>',block,re.S)
                if not tag or expected not in visible(tag.group(1)):
                    fail(f'{slug}: derived {expr} should display {expected}')

    budgets={'heroes':25*1024,'thumbs':18*1024,'og':200*1024}
    for folder,limit in budgets.items():
        for path in (ROOT/'images'/folder).glob('*'):
            if path.stat().st_size>limit: fail(f'oversize {path.relative_to(ROOT)}: {path.stat().st_size} bytes')
    for path in (ROOT/'figures').glob('*.svg.html'):
        if path.stat().st_size>6*1024: fail(f'oversize {path.relative_to(ROOT)}')

    colors=[('#0f172a','#ffffff',4.5,'light text'),('#64748b','#ffffff',4.5,'light muted'),('#1d6fd4','#ffffff',3,'light blue'),('#8b5cf6','#ffffff',3,'light purple'),('#f4f4f5','#27272a',4.5,'dark text'),('#a1a1aa','#27272a',4.5,'dark muted'),('#93c5fd','#27272a',3,'dark blue'),('#c4b5fd','#27272a',3,'dark purple')]
    for fg,bg,minimum,label in colors:
        r=ratio(fg,bg)
        if r<minimum: fail(f'contrast {label}: {r:.2f}:1')

    hashes={}
    for path in (ROOT/'images'/'heroes').glob('*.svg'):
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in hashes: fail(f'duplicate heroes: {path.name}, {hashes[digest]}')
        hashes[digest]=path.name

    first={}
    for item in ITEMS:
        key=hashlib.sha256(item['slug'].encode()).hexdigest()[:12]
        if key in first: fail(f'duplicate seeds: {item["slug"]}, {first[key]}')
        first[key]=item['slug']

    try: tracked=set(subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines())
    except Exception: tracked=set()
    if tracked:
        for path in html_files+list((ROOT/'assets').glob('*.css')):
            for rel in ref_pat.findall(path.read_text()):
                if rel not in tracked: fail(f'case/tracking mismatch: {path.name}: {rel}')

    print(f'Checked {len(ITEMS)} articles, {len(hashes)} heroes and {sum(1 for x in ITEMS if x["figure"])} figures.')
    for note in notes: print('NOTE',note)
    if errors:
        for error in errors: print('FAIL',error)
        print(f'FAILED: {len(errors)} problem(s)'); return 1
    print('PASS: image references, metadata, accessibility, budgets, contrast, variety and tracked path case.')
    return 0


if __name__=='__main__': raise SystemExit(main())
