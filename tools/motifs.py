"""Deterministic geometric motif library for The Med Frontier."""
from __future__ import annotations

import hashlib
import math
import random

BASE = "#0c1a3a"
PALETTES = {
    "AI": ("#1d6fd4", "#60a5fa", "#38bdf8"),
    "ANA": ("#7c3aed", "#a78bfa", "#38bdf8"),
    "MT": ("#0e7490", "#38bdf8", "#93c5fd"),
}


def seed_for(slug: str) -> int:
    return int(hashlib.sha256(slug.encode()).hexdigest()[:12], 16)


def _f(value: float) -> str:
    return f"{value:.1f}".rstrip("0").rstrip(".")


def motif_svg(slug: str, category: str, motifs: list[str], width: int, height: int) -> str:
    """Return compact, text-free SVG art with a quiet left third."""
    rng = random.Random(seed_for(slug))
    c1, c2, accent = PALETTES[category]
    x0 = width * .43
    cx = width * (.68 + rng.random() * .12)
    cy = height * (.42 + rng.random() * .16)
    parts = [f'<rect width="{width}" height="{height}" fill="{BASE}"/>']
    parts.append(f'<path d="M{x0:.0f} {height*.78:.0f} C{width*.56:.0f} {height*.18:.0f} {width*.76:.0f} {height*.9:.0f} {width*.98:.0f} {height*.24:.0f}" fill="none" stroke="{c1}" stroke-width="2" opacity=".28"/>')
    kind = seed_for("|".join(motifs)) % 6
    if kind == 0:
        for i in range(6):
            r = 34 + i * 24
            parts.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{r}" fill="none" stroke="{c2 if i%2 else c1}" stroke-width="{1.5+i%2}" opacity="{.22+i*.07:.2f}"/>')
    elif kind == 1:
        for row in range(3):
            for col in range(5):
                x = x0 + col * width*.095 + rng.randint(-8, 8)
                y = height*.18 + row * height*.26 + rng.randint(-7, 7)
                fill = accent if (row*5+col+seed_for(slug))%7 == 0 else c1
                parts.append(f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(width*.068)}" height="{_f(height*.17)}" rx="10" fill="{fill}" opacity="{.75 if fill==accent else .24}" stroke="{c2}" stroke-width="1.5"/>')
    elif kind == 2:
        pts=[]
        for i in range(8):
            x=x0+i*(width-x0)/8; y=cy+math.sin(i*1.55+rng.random())*height*.18
            pts.append((x,y))
        parts.append('<polyline points="'+' '.join(f'{_f(x)},{_f(y)}' for x,y in pts)+f'" fill="none" stroke="{c2}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
        for i,(x,y) in enumerate(pts):
            parts.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{9+(i%3)*2}" fill="{accent if i==seed_for(slug)%8 else c1}" stroke="{c2}" stroke-width="2"/>')
    elif kind == 3:
        for i in range(7):
            x=x0+(i%4)*width*.12; y=height*.2+(i//4)*height*.38+(i%2)*18
            r=width*.038
            pts=' '.join(f'{_f(x+r*math.cos(math.pi*j/3))},{_f(y+r*math.sin(math.pi*j/3))}' for j in range(6))
            parts.append(f'<polygon points="{pts}" fill="{c1}" fill-opacity=".16" stroke="{c2}" stroke-width="2"/>')
    elif kind == 4:
        for i in range(9):
            x=x0+i*(width-x0)/9
            h=height*(.12+.5*rng.random())
            parts.append(f'<rect x="{_f(x)}" y="{_f(cy-h/2)}" width="{_f(width*.052)}" height="{_f(h)}" rx="9" fill="{c1 if i%2 else c2}" opacity="{.3+i*.045:.2f}"/>')
        parts.append(f'<path d="M{x0:.0f} {cy:.0f} Q{width*.63:.0f} {height*.08:.0f} {width*.74:.0f} {cy:.0f} T{width*.98:.0f} {cy:.0f}" fill="none" stroke="{accent}" stroke-width="4"/>')
    else:
        for i in range(5):
            a=-2.4+i*.38; r=height*(.34+i*.065)
            x1=cx+math.cos(a)*r; y1=cy+math.sin(a)*r
            x2=cx+math.cos(a+2.0)*r; y2=cy+math.sin(a+2.0)*r
            parts.append(f'<path d="M{_f(x1)} {_f(y1)} A{_f(r)} {_f(r)} 0 0 1 {_f(x2)} {_f(y2)}" fill="none" stroke="{c2 if i%2 else c1}" stroke-width="{2+i}" opacity=".65"/>')
        parts.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="18" fill="{accent}" stroke="{c1}" stroke-width="4"/>')
    for i in range(18):
        x=x0+rng.random()*(width-x0-20); y=18+rng.random()*(height-36)
        parts.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{2+rng.randrange(4)}" fill="{accent}" opacity="{.14+rng.random()*.35:.2f}"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'+''.join(parts)+'</svg>\n'
