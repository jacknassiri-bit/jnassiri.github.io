# The Med Frontier

Static HTML for [themedfrontier.com](https://themedfrontier.com), published with GitHub Pages.

## New article publishing checklist

1. Copy `post-template.html` to a short, permanent `.html` filename. Fill in the title, deck, date, category, article body, citations, canonical URL, social metadata, and Article JSON-LD.
2. Create the 800, 1200, and 1600 pixel WebP hero files plus the 1200 × 630 share image in `images/`. Add the source, author, license, concepts, and selected concept to `images/CREDITS.md`.
3. Add the article card to `index.html`. Include its ISO `data-date`, filter category, responsive thumbnail, alt text, visible category label, deck, and reading time.
4. Add the same card and metadata to `all-articles.html` and the appropriate category page.
5. Add or update the article record in `search.html`.
6. Add the canonical article URL to `sitemap.xml` with the publication date.
7. Run `python3 scripts/check_site.py` and fix every failure before publishing.
8. Test the homepage, article, archive, category filter, search result, mobile menu, theme switch, citations, and share buttons at desktop and phone widths.

`EDITORIAL-AUDIT.md` and `WRITING-STANDARD.md` are excluded from the generated site by `_config.yml`. They remain visible in this public repository and its Git history.
