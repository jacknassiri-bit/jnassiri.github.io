#!/usr/bin/env python3
"""Capture every article, the home page and archive at two widths and themes."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tools'/'out'/'qa'


async def main():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise SystemExit('Playwright is not installed in this Python environment. Use the in-app Chromium QA run recorded in review/progress.md.')
    items=json.loads((ROOT/'tools'/'images.spec.json').read_text())
    pages=['index.html','all-articles.html']+[f'{x["slug"]}.html' for x in items]
    OUT.mkdir(parents=True,exist_ok=True)
    async with async_playwright() as p:
        browser=await p.chromium.launch()
        for width in (360,1440):
            for theme in ('light','dark'):
                page=await browser.new_page(viewport={'width':width,'height':1000})
                for name in pages:
                    await page.goto((ROOT/name).as_uri(),wait_until='networkidle')
                    await page.evaluate("t => { document.documentElement.dataset.theme=t; localStorage.setItem('theme',t) }",theme)
                    await page.screenshot(path=OUT/f'{Path(name).stem}-{width}-{theme}.png',full_page=True)
                    result=await page.evaluate("""() => ({overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(i=>!i.complete||!i.naturalWidth).length,minFigure:[...document.querySelectorAll('.fig text')].reduce((m,x)=>Math.min(m,parseFloat(getComputedStyle(x).fontSize)||99),99)})""")
                    if result['overflow'] or result['broken'] or result['minFigure']<11: raise RuntimeError(f'{name} {width} {theme}: {result}')
                await page.close()
        await browser.close()


if __name__=='__main__': asyncio.run(main())
