import fs from 'node:fs/promises';
import path from 'node:path';
import { articles } from './build_article_images.mjs';

const base = 'https://themedfrontier.com';
const oldBase = ['https://jacknassiri-bit.github.io','jnassiri.github.io'].join('/');
const articleSlugs = articles.map(item => item[0]);
const sitePages = ['index.html','all-articles.html','ai-medicine.html','anabolic-nutrition.html','about.html','contact.html','search.html','sources.html','how-i-write.html'];
const livePages = [...articleSlugs.map(slug => `${slug}.html`), ...sitePages];
const fallbackDescriptions = {
  'index.html':'Independent student writing on medical AI, health technology, training, supplements, and the research behind the claims.',
  'all-articles.html':'Every article from The Med Frontier, organized in one archive.',
  'ai-medicine.html':'Articles examining clinical AI studies, hospital workflows, medical devices, and patient outcomes.',
  'anabolic-nutrition.html':'Articles examining muscle growth, training, food, supplements, hormones, and the evidence behind fitness claims.',
  'about.html':'About Jack Nassiri, the student writer behind The Med Frontier.',
  'contact.html':'Contact Jack Nassiri about article ideas, research, or feedback for The Med Frontier.',
  'search.html':'Search every article published by The Med Frontier.',
  'sources.html':'The journals, databases, regulators, and research sources used by The Med Frontier.',
  'how-i-write.html':'How Jack Nassiri researches, checks, and writes articles for The Med Frontier.'
};

const decode = value => value
  .replace(/<[^>]+>/g,' ')
  .replace(/&amp;/g,'&').replace(/&quot;/g,'"').replace(/&#39;|&apos;/g,"'")
  .replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/\s+/g,' ').trim();
const isoDate = raw => {
  const date = new Date(`${decode(raw).replace(/\s*·.*$/,'')} 12:00:00`);
  if (Number.isNaN(date.getTime())) throw new Error(`Could not parse article date: ${raw}`);
  return date.toISOString().slice(0,10);
};
const canonicalFor = file => file === 'index.html' ? `${base}/` : `${base}/${file}`;

async function walk(dir) {
  const results = [];
  for (const entry of await fs.readdir(dir,{withFileTypes:true})) {
    if (entry.name === '.git') continue;
    const full = path.join(dir,entry.name);
    if (entry.isDirectory()) results.push(...await walk(full));
    else if (/\.(?:html|js|mjs|md|xml|txt|css)$/i.test(entry.name)) results.push(full);
  }
  return results;
}

for (const file of await walk('.')) {
  let text = await fs.readFile(file,'utf8');
  const next = text.replaceAll(oldBase,base).replace(new RegExp('(?:&amp;|&)via=' + 'TheMedFrontier','g'),'');
  if (next !== text) await fs.writeFile(file,next);
}

const sitemapDates = new Map();
for (const file of livePages) {
  let html = await fs.readFile(file,'utf8');
  const canonical = canonicalFor(file);
  const ogDescription = html.match(/<meta property="og:description" content="([^"]*)"/i)?.[1];
  const description = html.match(/<meta name="description" content="([^"]*)"/i)?.[1] || ogDescription || fallbackDescriptions[file];
  if (!description) throw new Error(`No description available for ${file}`);

  if (/<link rel="canonical"/i.test(html)) html = html.replace(/<link rel="canonical"[^>]*>/i, `<link rel="canonical" href="${canonical}">`);
  else html = html.replace(/(<meta name="viewport"[^>]*>)/i, `$1<link rel="canonical" href="${canonical}">`);
  if (/<meta name="description"/i.test(html)) html = html.replace(/<meta name="description"[^>]*>/i, `<meta name="description" content="${description}">`);
  else html = html.replace(/(<meta name="viewport"[^>]*>)/i, `$1<meta name="description" content="${description}">`);

  html = html.replace(/<script type="application\/ld\+json" data-site-schema>[\s\S]*?<\/script>/g,'');
  if (file === 'index.html') {
    const schema = { '@context':'https://schema.org', '@type':'WebSite', name:'The Med Frontier', url:`${base}/`, author:{'@type':'Person',name:'Jack Nassiri'}, description };
    html = html.replace('</head>', `<script type="application/ld+json" data-site-schema>${JSON.stringify(schema)}</script>\n</head>`);
  } else if (articleSlugs.includes(file.slice(0,-5))) {
    const slug = file.slice(0,-5);
    const headline = decode(html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i)?.[1] || '');
    const rawDate = html.match(/<div class="article-meta">[\s\S]*?<span>([^<]+)<\/span>/i)?.[1]
      || html.match(/<div class="meta">([^<]+)<\/div>/i)?.[1];
    if (!headline || !rawDate) throw new Error(`Missing headline/date in ${file}`);
    const datePublished = isoDate(rawDate);
    sitemapDates.set(file,datePublished);
    const schema = {
      '@context':'https://schema.org', '@type':'Article', headline, datePublished,
      author:{'@type':'Person',name:'Jack Nassiri'},
      image:`${base}/images/${slug}-share.webp`, mainEntityOfPage:canonical
    };
    html = html.replace('</head>', `<script type="application/ld+json" data-site-schema>${JSON.stringify(schema)}</script>\n</head>`);
  }
  await fs.writeFile(file,html);
}

const urls = livePages.map(file => {
  const loc = canonicalFor(file);
  const lastmod = sitemapDates.get(file) || '2026-09-18';
  return `  <url><loc>${loc}</loc><lastmod>${lastmod}</lastmod></url>`;
});
const sitemap = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`;
await fs.writeFile('sitemap.xml',sitemap);
console.log(`SEO metadata applied to ${livePages.length} live pages; sitemap contains ${livePages.length} URLs.`);
