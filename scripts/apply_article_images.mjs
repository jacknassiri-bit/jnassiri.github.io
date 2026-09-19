import fs from 'node:fs/promises';
import { articles } from './build_article_images.mjs';

console.log(`Applying image markup for ${articles.length} articles`);

const escAttr = value => String(value).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const imageMarkup = (slug, alt, loading='eager') => `<img src="images/${slug}-1600.webp" srcset="images/${slug}-800.webp 800w, images/${slug}-1200.webp 1200w, images/${slug}-1600.webp 1600w" sizes="100vw" width="1600" height="900" alt="${escAttr(alt)}"${loading === 'lazy' ? ' loading="lazy"' : ' fetchpriority="high"'}>`;

for (const [slug,,, ,alt] of articles) {
  const file = `${slug}.html`;
  let html = await fs.readFile(file,'utf8');
  if (!html.includes('site-images.css')) html = html.replace('</head>','<link rel="stylesheet" href="site-images.css">\n</head>');
  const figure = `<figure class="article-visual">${imageMarkup(slug,alt)}<figcaption>Original medical graphic by The Med Frontier · CC BY 4.0</figcaption></figure>`;
  html = html.replace(/<div class="hero" style="background-image:url\('[^']+'\)"><\/div>/, figure);
  html = html.replace(/<div class="article-hero" style="background-image:url\('[^']+'\)">\s*(?:<div class="hero-overlay"><\/div>)?\s*<\/div>/, figure);
  const imageUrl = `https://themedfrontier.com/images/${slug}-share.webp`;
  if (/<meta property="og:image"/.test(html)) html = html.replace(/<meta property="og:image"[^>]*>/, `<meta property="og:image" content="${imageUrl}">`);
  else html = html.replace(/(<meta property="og:description"[^>]*>)/, `$1<meta property="og:image" content="${imageUrl}">`);
  if (/<meta name="twitter:image"/.test(html)) html = html.replace(/<meta name="twitter:image"[^>]*>/, `<meta name="twitter:image" content="${imageUrl}">`);
  else html = html.replace(/<\/head>/, `<meta name="twitter:image" content="${imageUrl}">\n</head>`);
  await fs.writeFile(file, html);
}

for (const page of ['index.html','all-articles.html','ai-medicine.html','anabolic-nutrition.html']) {
  let html = await fs.readFile(page,'utf8');
  if (!html.includes('site-images.css')) html = html.replace('</head>','<link rel="stylesheet" href="site-images.css">\n</head>');
  for (const [slug,,, ,alt] of articles) {
    const href = `${slug}.html`.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
    const card = new RegExp(`(<a\\b[^>]*href=["']${href}["'][^>]*>(?:(?!<\\/a>)[\\s\\S])*?)(<div class=["']((?:post-thumb|card-thumb)[^"']*)["'][^>]*>[\\s\\S]*?<\\/div>)`,'g');
    html = html.replace(card, (_m, before, _old, classes) => `${before}<div class="${classes}">${imageMarkup(slug,alt,'lazy')}</div>`);
  }
  if (page === 'index.html') {
    html = html.replace(/\s*<img class="featured-thumb"[^>]*>/g, '');
    html = html.replace(/(<a class="featured-card" href="ai-liver-cancer-second-reader\.html">)/, `$1\n        <img class="featured-thumb" src="images/ai-liver-cancer-second-reader-800.webp" srcset="images/ai-liver-cancer-second-reader-800.webp 800w, images/ai-liver-cancer-second-reader-1200.webp 1200w" sizes="(max-width: 768px) 100vw, 42vw" width="800" height="450" alt="Liver CT schematic with a highlighted lesion and second-reader marker">`);
    const homeImage = 'https://themedfrontier.com/images/the-med-frontier-share.webp';
    if (/<meta property="og:image"/.test(html)) html = html.replace(/<meta property="og:image"[^>]*>/, `<meta property="og:image" content="${homeImage}">`);
    else html = html.replace(/(<meta property="og:description"[^>]*>)/, `$1<meta property="og:image" content="${homeImage}">`);
    if (/<meta name="twitter:image"/.test(html)) html = html.replace(/<meta name="twitter:image"[^>]*>/, `<meta name="twitter:image" content="${homeImage}">`);
    else html = html.replace(/<\/head>/, `<meta name="twitter:image" content="${homeImage}">\n</head>`);
  }
  await fs.writeFile(page, html);
}
console.log('Image markup applied');
