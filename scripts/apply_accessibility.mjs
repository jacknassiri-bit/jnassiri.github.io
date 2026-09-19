import fs from 'node:fs/promises';

const files = (await fs.readdir('.')).filter(file => file.endsWith('.html'));
let updated = 0;
for (const file of files) {
  let html = await fs.readFile(file,'utf8');
  if (!/<nav\b/.test(html)) continue;
  if (!html.includes('site-accessibility.css')) html = html.replace('</head>','<link rel="stylesheet" href="site-accessibility.css">\n</head>');
  if (!html.includes('site-theme.js')) html = html.replace(/<\/head>/,'<script src="site-theme.js"></script>\n</head>');
  if (!html.includes('class="skip-link"')) html = html.replace(/<body([^>]*)>/,`<body$1><a class="skip-link" href="#main-content">Skip to main content</a>`);
  if (!html.includes('id="main-content"')) {
    if (/<main\b/.test(html)) html = html.replace(/<main(\s|>)/,'<main id="main-content" tabindex="-1"$1');
    else if (/<div class="article-wrap"/.test(html)) html = html.replace('<div class="article-wrap"','<div id="main-content" tabindex="-1" class="article-wrap"');
    else if (/<section class="hero"/.test(html)) html = html.replace('<section class="hero"','<section id="main-content" tabindex="-1" class="hero"');
    else html = html.replace(/<body([^>]*)>/,`<body$1 id="main-content" tabindex="-1">`);
  }
  await fs.writeFile(file,html);
  updated += 1;
}
console.log(`Accessibility shell applied to ${updated} pages.`);
