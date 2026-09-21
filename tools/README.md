# Image generator

`build_images.py` reads `images.spec.json` and creates the article heroes, card thumbnails, inline figure snippets and social cards. The artwork is deterministic, geometric and fully local. The live site uses the committed outputs and does not run Python.

Requirements: Python 3, Pillow, Playwright with Chromium for the optional browser QA, and local copies of the families named by `--font-display`, `--font-ui` and `--font-wordmark` in `assets/typography.css`. This machine uses local Georgia and Arial fallbacks for the PNG cards because the web fonts are not installed as files.

Commands:

```sh
python tools/build_images.py
python tools/build_images.py --skip-og
python tools/build_images.py --og-only
python tools/check_images.py
python tools/qa_screenshots.py
```

To add an article: add its slug, category, title, motifs and figure spec (or `null`) to `images.spec.json`; run the build; add the hero markup, thumbnail URL, figure snippet and meta tags described in the image brief; run the checks; commit the outputs.
