import fs from 'node:fs/promises';

let html = await fs.readFile('index.html','utf8');
const articleDates = new Map();
for (const match of html.matchAll(/<a\b[^>]*href="([^"]+\.html)"[^>]*class="post-card"[\s\S]*?<\/a>/g)) {
  const file = match[1];
  const article = await fs.readFile(file,'utf8');
  const published = article.match(/"datePublished":"(\d{4}-\d{2}-\d{2})"/)?.[1];
  if (!published) throw new Error(`No datePublished found in ${file}`);
  articleDates.set(file,published);
}

const gridPattern = /(<div class="posts-grid">)\s*([\s\S]*?)\s*(<\/div>\s*<\/section>)/;
const gridMatch = html.match(gridPattern);
if (!gridMatch) throw new Error('Homepage posts grid was not found');
const cards = [...gridMatch[2].matchAll(/<a\b[^>]*href="([^"]+\.html)"[^>]*class="post-card"[\s\S]*?<\/a>/g)].map(match => {
  const file = match[1];
  let card = match[0];
  card = card.replace(/\sdata-date="[^"]*"/,'');
  card = card.replace(/\shidden(?=[ >])/,'');
  card = card.replace('class="post-card"',`class="post-card" data-date="${articleDates.get(file)}"`);
  card = card.replace('data-category="Med Tech"','data-category="AI in Medicine"');
  return { file, date:articleDates.get(file), html:card };
}).sort((a,b) => b.date.localeCompare(a.date));
cards.forEach((card,index) => {
  if (index >= 9) card.html = card.html.replace('class="post-card"','class="post-card" hidden');
});

html = html.replace(gridPattern,`${gridMatch[1]}\n\n        ${cards.map(card => card.html).join('\n        ')}\n\n      ${gridMatch[3]}`);

const latest = cards[0];
const latestTitle = latest.html.match(/<h3>([\s\S]*?)<\/h3>/)?.[1];
const latestDescription = latest.html.match(/<p>([\s\S]*?)<\/p>/)?.[1];
const latestTag = latest.html.match(/<div class="post-tag[^>]*>([\s\S]*?)<\/div>/)?.[1];
const latestRead = latest.html.match(/<div class="post-foot">[\s\S]*?<span>[^<]+<\/span><span>·<\/span><span>([^<]+)<\/span>/)?.[1];
const rawLatestImage = latest.html.match(/<img[^>]+>/)?.[0];
const latestImage = rawLatestImage.includes('class="') ? rawLatestImage.replace('class="','class="featured-thumb ') : rawLatestImage.replace('<img ','<img class="featured-thumb" ');
const fullDate = new Intl.DateTimeFormat('en-US',{month:'long',day:'numeric',year:'numeric',timeZone:'UTC'}).format(new Date(`${latest.date}T12:00:00Z`));

html = html.replace(/<a href="[^"]+" class="hero-btn">Read the latest →<\/a>/,`<a href="${latest.file}" class="hero-btn">Read the latest →</a>`);
html = html.replace(/<a class="featured-card" href="[^"]+">[\s\S]*?<\/a>/,`<a class="featured-card" href="${latest.file}">
        ${latestImage}
        <div class="fc-tag">${latestTag}</div>
        <h2>${latestTitle}</h2>
        <p>${latestDescription}</p>
        <div class="fc-meta"><span>${fullDate}</span><span>·</span><span>${latestRead}</span></div>
      </a>`);
if (!html.includes('Newsletter submissions are sent to the configured Formspree endpoint.')) html = html.replace(/(<form class="nl-form"[^>]*>)/,'<!-- Newsletter submissions are sent to the configured Formspree endpoint. -->\n        $1');

await fs.writeFile('index.html',html);
console.log(`Homepage sorted ${cards.length} cards; newest article is ${latest.file} (${latest.date}).`);
