# The Med Frontier — Setup Guide
> Where AI meets the human body.

## Your files
- `index.html` — homepage
- `about.html` — about page  
- `post-template.html` — copy this for every new post
- `README.md` — this guide

---

## How to publish on GitHub Pages

### Step 1 — Create your repository
1. Go to github.com and sign in
2. Click **+** (top right) → "New repository"
3. Name it: `your-username.github.io`
4. Set to **Public**
5. Click "Create repository"

### Step 2 — Upload your files
1. On the new repo page, click **"uploading an existing file"**
2. Drag all 4 files into the upload box
3. Click **"Commit changes"**

### Step 3 — Enable GitHub Pages
1. Go to repo → **Settings** → **Pages**
2. Source: "Deploy from a branch"
3. Branch: **main**, folder: **/ (root)**
4. Click **Save**

### Step 4 — You're live
Wait ~2 minutes, then visit `https://your-username.github.io`

---

## Writing a new post

1. Duplicate `post-template.html`
2. Rename it (e.g. `ai-drug-discovery.html`)
3. Edit everything marked `<!-- CHANGE THIS -->`
4. Write your post between the comment markers
5. Upload the new file to GitHub
6. Add a card for it in `index.html` (copy an existing post card block)

## Draft vs. Published
In each post card in `index.html`, find:
```html
<span class="status s-draft">Draft</span>
```
Change `s-draft` to `s-pub` and "Draft" to "Published" when ready to go live.

---

## Weekly content calendar

| Week | Pillar | Topic |
|------|--------|-------|
| 1 | AI in Medicine | Can AI outdiagnose a radiologist? |
| 2 | Med Tech | The new wave of robotic surgery |
| 3 | AI in Medicine | How AI is accelerating drug discovery |
| 4 | Med Tech | Wearable biosensors: what's coming |
| 5 | AI in Medicine | LLMs in the clinic |
| 6 | Med Tech | CRISPR in 2026 |

## Sources to check every week
- FDA device approvals: fda.gov/medical-devices
- STAT News: statnews.com
- NIH News: nih.gov/news-events
- Nature Medicine: nature.com/nm
- The Lancet: thelancet.com
