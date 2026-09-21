#!/usr/bin/env python3
"""Build deterministic heroes, thumbnails, inline figures and social cards."""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
from pathlib import Path

from motifs import BASE, PALETTES, motif_svg, seed_for

ROOT = Path(__file__).resolve().parents[1]
SPEC = Path(__file__).with_name("images.spec.json")


FIG = {
"medical-ai-real-world": ("Did the AI result reach the patient?", "Across four clinical studies, two systems changed workflow or detection while two did not change the measured patient pathway.", [
    ("Kenya LLM · 9,691 patients", "2.2% AI vs 2.0% control · NO CHANGE"),
    ("LungIMPACT · 93,326 X-rays", "CT 53 vs 53 days · diagnosis 44 vs 46 days · NO CHANGE"),
    ("Spain mammography · 31,301 women", "workload −63.6% · detection 6.3 to 7.3 per 1,000 · CHANGED"),
    ("LiON · 10,333 patients", "51 lesions · 15 malignancies · CHANGED")], "The result reached the workflow in two of the four studies. (Agweyu et al.; Woznitza et al.; Elías-Cabot et al.; Kuo et al.)"),
"ai-liver-cancer-second-reader": ("What LiON caught", "Among 10,333 patients, the system found 51 overlooked lesions, including 15 malignancies; 37 reports were amended and 22 cases were escalated.", [("10,333", "patients read"),("51", "overlooked lesions"),("15", "malignancies"),("37 amended reports", "22 multidisciplinary escalations")], "The funnel narrowed from 10,333 patients to 15 overlooked malignancies. (Kuo et al.)"),
"ai-designed-drug-rentosertib": ("Forced vital capacity at 12 weeks", "In the secondary result among 71 participants, forced vital capacity changed by plus 98.4 milliliters with 60 milligrams once daily and minus 20.3 milliliters with placebo over 12 weeks.", [("+98.4 mL", "60 mg once daily"),("−20.3 mL", "placebo"),("71 participants", "12 weeks · secondary result")], "The 60 mg group gained 98.4 mL while the placebo group lost 20.3 mL over 12 weeks. (Richeldi et al.)"),
"ai-mammography-autonomous": ("Workload, detection and recall", "Radiologist workload fell 63.6 percent, detection rose from 6.3 to 7.3 cancers per 1,000 examinations, and recall rose 14.8 percent relative to standard screening.", [("−63.6%", "radiologist workload"),("6.3 → 7.3", "cancers per 1,000"),("+14.8%", "recall rate, relative")], "Workload fell sharply while detection and recall both rose. (Elías-Cabot et al.)"),
"beta-alanine-endurance": ("Where beta-alanine showed a signal", "Studies under 60 seconds showed no clear benefit; effects were more consistent from 60 to 240 seconds, with the largest practical signal from 0.5 to 10 minutes and a median improvement around 2.85 percent.", [("under 60 s", "no clear benefit"),("60–240 s", "improved more consistently"),("0.5–10 min", "largest practical signal"),("about 2.85%", "median improvement")], "The clearest signal appeared in hard efforts lasting roughly one to several minutes. (Hobson et al.; Saunders et al.)"),
"ai-sepsis-alerts": ("Median triage-to-antibiotic time", "Median time was 46 minutes among 256 patients with the alert and 50 minutes among 318 control patients; one-hour and three-hour antibiotic rates also improved.", [("46 min", "AI alert · 256 patients"),("50 min", "control · 318 patients"),("4 minutes", "difference")], "The median difference was four minutes, and one-hour and three-hour antibiotic rates also improved. (Kijpaisalratana et al.)"),
"sarms-risk": ("What was inside 44 online products", "About half of the 44 products bought online contained a selective androgen receptor modulator and the rest did not.", [("ABOUT HALF", "contained a SARM"),("THE REST", "did not")], "About half of the 44 products contained a SARM. (Cohen et al.)"),
"ai-cancer-screening": ("Reading workload in the MASAI trial", "In a trial of more than 80,000 women, AI-supported reading used about 56 units of work for every 100 in standard reading, a 44 percent reduction, while finding at least as many cancers.", [("STANDARD · 100", "reading workload"),("AI-SUPPORTED · ABOUT 56", "44% lower · at least as many cancers found")], "AI-supported screening cut reading workload by about 44% while finding at least as many cancers. (Lang et al.)"),
"caffeine-performance": ("Caffeine before bed", "A 400 milligram dose reduced sleep when taken at bedtime, three hours before bed and even six hours before bed.", [("BEDTIME", "400 mg"),("3 h before", "400 mg"),("6 h before", "even this one reduced sleep")], "A 400 mg dose still reduced sleep when taken six hours before bed. (Drake et al.)"),
"protein-muscle-growth": ("Daily protein range", "The ISSN range spans 1.4 to 2.0 grams per kilogram per day on a scale from zero to 2.5 grams per kilogram per day.", [("0", "1.4"),("1.4–2.0 g/kg/day", "enough for most people who lift"),("2.5", "")], "For most people who lift, the useful daily range is 1.4 to 2.0 g/kg. (Jäger et al.)"),
"hgh-muscle-growth": ("Measured lean mass and performance", "Growth hormone increased lean body mass by 2.1 kilograms compared with control while strength and exercise capacity showed no clear improvement.", [("+2.1 kg", "lean body mass vs control"),("FLAT", "strength and exercise capacity · no clear improvement")], "Lean body mass rose by 2.1 kg, while strength and exercise capacity did not clearly improve. (Liu et al.)"),
"robotic-surgery": ("The cost and reach of robotic surgery", "Robotic surgery has been in use since 2000, is found in roughly 70 percent of major U.S. hospitals, costs about 2 million dollars to buy, and more than 100,000 dollars a year to maintain.", [("SINCE 2000", "in use"),("ROUGHLY 70%", "of major US hospitals"),("ABOUT $2 MILLION", "to purchase"),("OVER $100,000", "a year to maintain")], "Robotic systems are common and expensive."),
"crispr-2026": ("Casgevy trial result", "Twenty-nine of 31 evaluable patients avoided severe pain crises for at least 12 months; the treatment costs 2.2 million dollars.", [("29 OF 31", "avoided severe pain crises for at least 12 months"),("$2.2 MILLION", "treatment cost")], "Twenty-nine of 31 evaluable patients avoided severe pain crises for at least 12 months. (Frangoul et al.)"),
"next-gen-imaging": ("Diagnostic novice scans", "In a 240-patient study, left ventricular size, function and pericardial effusion were diagnostic in 237 of 240 cases, or 98.75 percent; right ventricular size was diagnostic in 222 of 240, or 92.5 percent.", [("237 of 240 · 98.75%", "LV size, function and pericardial effusion"),("222 of 240 · 92.5%", "right ventricular size"),("8 nurses", "without prior echocardiography experience")], "Novice scans were diagnostic in 237 of 240 and 222 of 240 cases for the listed measures. (Narula et al.)"),
"llms-clinic": ("A safer division of work", "The model can retrieve, organize, suggest and draft; the clinician keeps the final diagnosis, doses, treatment choice and patient explanation.", [("LET THE MODEL", "retrieve a guideline · organize a chart · suggest questions · draft a note"),("KEEP WITH THE CLINICIAN", "final diagnosis · medication doses · treatment choice · explain it to the patient")], "Schematic: The model prepares information while the clinician owns the medical decision."),
"ai-replacing-radiologists": ("How imaging work is divided", "AI can flag, prioritize, detect and draft; the radiologist compares prior images, uses history, decides what changes care and owns the report.", [("AI DOES TODAY", "flag a stroke · prioritize a chest X-ray · detect a lung nodule · draft a report"),("RADIOLOGIST STILL DOES", "compare earlier images · use history · decide what changes care · own the report")], "Schematic: AI handles narrow imaging tasks while the radiologist owns the clinical reading."),
"medical-chatbots-danger": ("The missing clinical context", "The chatbot sees a typed message while the clinician can use the chart, exam, allergies, medications and a follow-up question.", [("WHAT THE CHATBOT SEES", "the typed message"),("WHAT THE CLINICIAN SEES", "chart · exam · allergies · medications · the follow-up question")], "Schematic: A typed message leaves out information a clinician can check."),
"ai-heart-attack-prediction": ("A risk score needs an action", "A useful risk score leads to one named next step, such as treating LDL, managing blood pressure or ordering the follow-up scan; a score with no plan is a dead end.", [("RISK SCORE", "treat LDL"),("NEXT STEP", "manage blood pressure · order the follow-up scan"),("DEAD END", "score with no plan")], "Schematic: A risk score is useful when it leads to a specific clinical action."),
"smart-implants": ("Who receives the alert", "The alert moves from an implant through a home hub or phone to a clinic queue and clinician action; fluid buildup may be detected up to two weeks before severe symptoms.", [("IMPLANT", "home hub or phone"),("CLINIC QUEUE", "urgent alert waits in the queue"),("CLINICIAN ACTION", "fluid buildup up to two weeks before severe symptoms")], "Schematic: A smart implant still depends on the clinic responding to its alert."),
"ai-drug-discovery": ("Where AI evidence exists in the drug pipeline", "Evidence for AI is strongest in target and molecule work; preclinical testing, phase 1 to 3 trials and approval remain ahead, while AlphaFold has predicted over 200 million structures.", [("EVIDENCE SO FAR", "target → molecule"),("STILL AHEAD", "preclinical → phase 1 to 3 → approval"),("ALPHAFOLD", "over 200 million predicted structures")], "Schematic: AI has its strongest evidence early in the drug pipeline."),
}


def _figure(slug: str, category: str) -> str:
    title, desc, rows, caption = FIG[slug]
    color = "p" if category == "ANA" else "b"
    h = min(350, 92 + len(rows) * 58)
    out = [f'<figure class="fig">\n<svg viewBox="0 0 420 {h}" role="img" aria-labelledby="fig-{slug}-t fig-{slug}-d">',
           f'<title id="fig-{slug}-t">{html.escape(title)}</title>', f'<desc id="fig-{slug}-d">{html.escape(desc)}</desc>',
           f'<rect class="panel" x="1" y="1" width="418" height="{h-2}" rx="12"/>',
           f'<text class="t" x="20" y="30" font-size="15" font-weight="700">{html.escape(title)}</text>']
    y = 56
    for i, (label, note) in enumerate(rows):
        out.append(f'<rect class="{color}" x="20" y="{y}" width="{8 + (seed_for(slug+str(i))%85)}" height="8" rx="4" opacity=".85"/>')
        derived = ''
        if slug == "ai-cancer-screening" and i == 1: derived = ' data-derived="100-44"'
        if slug == "next-gen-imaging" and i < 2: derived = f' data-derived="{("237/240","222/240")[i]}"'
        out.append(f'<text class="t mono" x="20" y="{y+27}" font-size="13" font-weight="700"{derived}>{html.escape(label)}</text>')
        if note:
            words = note.split(" · ")
            out.append(f'<text class="tm" x="190" y="{y+27}" font-size="12.5">{html.escape(words[0])}</text>')
            if len(words) > 1:
                out.append(f'<text class="tm" x="190" y="{y+44}" font-size="12.5">{html.escape(" · ".join(words[1:]))}</text>')
        y += 58
    out.append(f'</svg>\n<figcaption>{html.escape(caption)}</figcaption>\n</figure>\n')
    return "\n".join(out)


def _font(path_options, size):
    from PIL import ImageFont
    for path in path_options:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def _og(item: dict, path: Path) -> None:
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (1200, 630), BASE)
    d = ImageDraw.Draw(im)
    c1, c2, accent = PALETTES[item["category"]]
    display = _font(["/System/Library/Fonts/NewYork.ttf", "/System/Library/Fonts/Supplemental/Georgia.ttf"], 58)
    ui = _font(["/System/Library/Fonts/HelveticaNeue.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"], 24)
    wordmark = _font(["/System/Library/Fonts/Supplemental/Georgia Bold.ttf"], 27)
    d.rounded_rectangle((64, 54, 270, 96), 20, fill=c1)
    chip = {"AI":"AI IN MEDICINE","ANA":"ANABOLICS","MT":"MED TECH"}[item["category"]]
    d.text((82, 62), chip, font=ui, fill="white")
    words=item["title"].split(); lines=[]; current=""
    for word in words:
        trial=(current+" "+word).strip()
        if d.textlength(trial,font=display)>690 and current: lines.append(current); current=word
        else: current=trial
    if current: lines.append(current)
    while len(lines)>3:
        lines[-2]+=" "+lines.pop()
    for i,line in enumerate(lines[:3]): d.text((64, 142+i*70), line, font=display, fill="white")
    rng=__import__("random").Random(seed_for(item["slug"]))
    for i in range(12):
        x=790+rng.randint(0,340); y=90+rng.randint(0,430); r=10+rng.randint(0,55)
        d.ellipse((x-r,y-r,x+r,y+r), outline=c2 if i%2 else accent, width=4)
        if i: d.line((x,y,790+rng.randint(0,340),90+rng.randint(0,430)),fill=c1,width=3)
    d.text((64, 548), "The Med", font=wordmark, fill="white")
    x=64+d.textlength("The Med ",font=wordmark)
    d.text((x,548), "Frontier", font=wordmark, fill=accent)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.quantize(colors=128).save(path, optimize=True)


def _default_og(path: Path) -> None:
    item={"slug":"default","category":"AI","title":"Where AI meets the human body.","motifs":[]}
    _og(item,path)


def _apple_icon(path: Path) -> None:
    """Raster counterpart of favicon.svg, drawn from the same coordinates."""
    from PIL import Image, ImageDraw
    scale = 180 / 32
    im = Image.new("RGB", (180, 180), "#080c10")
    d = ImageDraw.Draw(im)
    pts = [(2,16),(7,16),(10,8),(13,24),(16,11),(19,21),(22,16),(30,16)]
    d.line([(round(x*scale),round(y*scale)) for x,y in pts], fill="#38bdf8", width=12, joint="curve")
    path.parent.mkdir(parents=True,exist_ok=True)
    im.save(path,optimize=True)


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--skip-og",action="store_true"); ap.add_argument("--og-only",action="store_true")
    args=ap.parse_args(); items=json.loads(SPEC.read_text())
    if not args.og_only:
        for item in items:
            for sub,w,h in (("heroes",1600,420),("thumbs",900,300)):
                p=ROOT/"images"/sub/f'{item["slug"]}.svg'; p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(motif_svg(item["slug"],item["category"],item["motifs"],w,h))
            if item["figure"]:
                p=ROOT/"figures"/f'{item["slug"]}.svg.html'; p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(_figure(item["slug"],item["category"]))
    if not args.skip_og:
        try:
            for item in items: _og(item,ROOT/"images"/"og"/f'{item["slug"]}.png')
            _default_og(ROOT/"images"/"og"/"default.png")
            _apple_icon(ROOT/"images"/"icons"/"apple-touch-icon.png")
        except ImportError:
            print("Pillow is required for OG cards", file=sys.stderr); raise


if __name__ == "__main__": main()
