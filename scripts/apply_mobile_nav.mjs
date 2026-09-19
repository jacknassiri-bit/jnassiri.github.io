import fs from 'node:fs/promises';
import path from 'node:path';

const files = (await fs.readdir('.')).filter(file => file.endsWith('.html'));
let updated = 0;
for (const file of files) {
  let html = await fs.readFile(file, 'utf8');
  if (!/<nav\b/.test(html) || !/class="nav-links"/.test(html)) continue;
  if (!html.includes('site-nav.css')) html = html.replace('</head>', '<link rel="stylesheet" href="site-nav.css">\n<script src="site-nav.js" defer></script>\n</head>');
  html = html.replace(/<ul class="nav-links"(?![^>]*\bid=)/, '<ul class="nav-links" id="primary-navigation">');
  if (!html.includes('class="menu-toggle"')) {
    html = html.replace(/(<div class="nav-right">\s*)/, '$1<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-navigation" aria-label="Open navigation menu"><span class="menu-toggle-lines" aria-hidden="true"></span></button>');
  }
  await fs.writeFile(file, html);
  updated += 1;
}
console.log(`Mobile navigation applied to ${updated} pages.`);
