import fs from 'node:fs/promises';

const disclaimer = 'The Med Frontier is written by a high school student for education. It is not medical advice. Talk to a doctor before changing medication, supplements, or training.';
const files = (await fs.readdir('.')).filter(file => file.endsWith('.html'));
let footers = 0;
let articles = 0;

for (const file of files) {
  let html = await fs.readFile(file,'utf8');
  if (!/<footer\b/.test(html)) continue;
  if (!html.includes('site-disclaimer.css')) html = html.replace('</head>','<link rel="stylesheet" href="site-disclaimer.css">\n</head>');
  if (!html.includes('footer-disclaimer')) html = html.replace(/<footer([^>]*)>/,`<footer$1><p class="site-disclaimer footer-disclaimer">${disclaimer}</p>`);
  footers += 1;

  if (html.includes('"@type":"Article"') && !html.includes('article-disclaimer')) {
    const notice = `<aside class="site-disclaimer article-disclaimer" aria-label="Medical disclaimer">${disclaimer}</aside>`;
    if (/<div class="share-section"/.test(html)) html = html.replace(/<div class="share-section"/,`${notice}\n    <div class="share-section"`);
    else html = html.replace('</article>',`</article>${notice}`);
    articles += 1;
  }
  await fs.writeFile(file,html);
}
console.log(`Disclaimer added to ${footers} footers and ${articles} article share areas.`);
