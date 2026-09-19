import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);

export const articles = [
  ['medical-ai-real-world','Clinical AI in hospitals','Two real-world trials','clinical','Chest X-ray worklist beside a hospital outcome chart',['Chest X-ray worklist with outcome chart','Hospital workflow timeline','Two-trial comparison graphic']],
  ['ai-liver-cancer-second-reader','LiON liver CT review','15 malignancies found','liver','Liver CT schematic with a highlighted lesion and second-reader marker',['Annotated liver CT slice','Second-reader review screen','Liver lesion workflow']],
  ['fda-testing-generative-medical-ai','FDA medical AI testing','Benchmark → clinic → monitoring','document','FDA-style evaluation document with three testing stages',['Regulatory checklist','Three-stage evaluation path','Postmarket monitoring dashboard']],
  ['ai-designed-drug-rentosertib','Rentosertib phase 2a','71 participants · 12 weeks','molecule','Molecular structure flowing into a pulmonary fibrosis trial chart',['Rentosertib molecule and lung chart','TNIK target diagram','Phase 2a dose groups']],
  ['ai-mammography-autonomous','Autonomous mammography','63.6% less reading work','mammogram','Mammogram screen with low-risk scans routed past a reading queue',['Mammogram triage screen','Low-risk routing diagram','Detection and recall chart']],
  ['beta-alanine-endurance','Beta-alanine and carnosine','Best support: 1–4 minutes','supplement','Supplement scoop beside an exercise-duration performance curve',['Carnosine buffering diagram','Exercise-duration curve','Beta-alanine scoop and timer']],
  ['ai-sepsis-alerts','Sepsis early warning','590,736 patients monitored','monitor','Bedside vital-sign monitor with a sepsis alert marker',['Bedside sepsis alert','Vital-sign trend panel','Alert-to-antibiotic timeline']],
  ['testosterone-muscle','Testosterone and muscle','43-person controlled trial','muscle','Dumbbell and muscle measurement chart with four study groups',['Four-group trial chart','Muscle and hormone pathway','Strength measurement graphic']],
  ['ai-heart-attack-prediction','Cardiovascular risk AI','Retina + coronary CT','heart','Heart and retinal vessels connected to a risk curve',['Retinal vessels and heart','Coronary plaque scan','Risk-score action pathway']],
  ['sarms-risk','SARMs product risk','44 products tested','vial','Rows of supplement bottles with mismatched contents',['44-product label audit','SARM vial and warning card','Androgen receptor diagram']],
  ['ai-cancer-screening','Cancer screening AI','80,000+ in MASAI','screening','Breast screening panels with detection and recall counters',['Mammography recall dashboard','Screening flow diagram','Detection versus false-positive chart']],
  ['protein-timing','Protein timing','Daily total comes first','protein','Four protein meals distributed across a day timeline',['Meal distribution clock','Protein meals across a school day','Post-workout timing window']],
  ['medical-chatbots-danger','Medical chatbot safety','One missing detail changes the answer','chat','Patient message with a missing clinical detail highlighted',['Chat with missing context','Safe and unsafe prompt comparison','Clinician review handoff']],
  ['ai-replacing-radiologists','Radiology workflow','Scan + history + responsibility','radiology','Multiple scan panels leading to a radiologist report',['Radiology worklist','Multi-finding chest CT','AI flag with final report']],
  ['caffeine-performance','Caffeine dose and sleep','400 mg affected sleep at 6 hours','caffeine','Coffee cup beside a dose and sleep timeline',['Caffeine half-life timeline','Dose-response cup graphic','Evening workout and sleep clock']],
  ['sleep-testosterone','Sleep and testosterone','One week of 5-hour nights','sleep','Seven-night sleep timeline beside a hormone curve',['Seven-night sleep study','Sleep clock and hormone curve','School-night schedule']],
  ['ozempic-muscle-loss','GLP-1 weight loss','Track strength with the scale','scale','Scale showing fat and lean-mass change beside a strength gauge',['Body-composition scale','Injection with strength gauge','Weight and function timeline']],
  ['bpc157-peptides','BPC-157 evidence gap','Animal data · little human evidence','peptide','Peptide chain above an empty human-trial panel',['Animal-to-human evidence gap','Peptide vial and tendon','Trial evidence ladder']],
  ['supplements-evidence','Supplement evidence','Study · dose · useful outcome','evidence','Supplement label compared with a research paper and measured outcome',['Label-to-study comparison','Evidence-ranked gym bag','Dose and outcome checklist']],
  ['protein-muscle-growth','Protein for muscle','About 1.6 g/kg in meta-analysis','protein','Protein meals and a muscle-growth response curve',['Protein response curve','Meal portions across a day','Training plus protein diagram']],
  ['hgh-muscle-growth','HGH and lean mass','+2.1 kg · no strength gain','hormone','Lean-mass bar rising while the strength bar stays level',['Lean mass versus strength chart','HGH vial and outcome bars','Body-composition scan']],
  ['ai-hospital-triage','Emergency triage AI','Risk score with nurse override','triage','Emergency department queue with a nurse override control',['Emergency queue dashboard','Nurse override screen','Triage priority ladder']],
  ['creatine-guide','Creatine monohydrate','Repeated high-intensity work','creatine','Creatine scoop beside ATP recycling arrows and repeated sets',['ATP recycling diagram','Creatine scoop and repeated sets','Monohydrate evidence card']],
  ['ambient-ai-scribes','Ambient AI scribe','Draft note · doctor review','scribe','Clinical conversation flowing into a reviewed draft note',['Visit-to-note workflow','Microphone and clinical note','Doctor review screen']],
  ['carbs-training','Carbohydrates and training','Fuel matched to workload','carbs','Carbohydrate meal beside a training-energy curve',['Practice-day meal timeline','Glycogen fuel gauge','Carbohydrate plate and workout']],
  ['lean-bulk','Lean bulk','Slow trend · stronger lifts','bulk','Body-weight trend rising slowly beside a strength log',['Weight and strength trend','Small calorie surplus dial','Weekly weigh-in average']],
  ['sleep-muscle-growth','Sleep and muscle growth','Time in bed supports adaptation','sleep','Bed and recovery curve across repeated training days',['Training and recovery timeline','Sleep window on school nights','Recovery curve']],
  ['robotic-surgery','Robotic surgery','Surgeon controls every movement','robotic','Surgeon console linked to articulated instruments at an operating table',['Console-to-instrument diagram','Robotic arm in laparoscopy','Experience learning curve']],
  ['ai-drug-discovery','AI drug discovery','Search faster · trials still decide','discovery','Candidate molecules passing through a discovery funnel into trials',['Drug discovery funnel','Protein structure to molecule','Candidate attrition chart']],
  ['wearable-biosensors','Wearable biosensors','Signal → decision','wearable','Smartwatch waveform flowing into a clinician review panel',['Watch ECG and clinician review','Continuous glucose trace','Signal uncertainty panel']],
  ['llms-clinic','LLMs in the clinic','86.5% exam accuracy','llm','Clinical note draft beside a physician approval panel',['LLM draft and approval','Exam score versus clinic','Chart summary workflow']],
  ['crispr-2026','CRISPR treatment','29 of 31 avoided pain crises','dna','DNA strand cut at a marked site beside a treatment result',['CRISPR cut-site diagram','Blood stem-cell editing path','29-of-31 outcome chart']],
  ['ai-pathology','AI in pathology','Highlight the suspicious region','pathology','Digital pathology slide with a small suspicious region outlined',['Annotated histology slide','Slide scanner and review','Suspicious-region heatmap']],
  ['smart-implants','Connected implants','Alert needs a destination','implant','Implanted cardiac sensor sending a signal to a clinic dashboard',['Cardiac implant alert path','Remote monitoring dashboard','Connection failure backup']],
  ['next-gen-imaging','Next-generation imaging','CT · MRI · ultrasound','imaging','Three imaging panels for photon-counting CT, MRI and ultrasound',['Three-modality comparison','Photon-counting detector','Portable MRI at bedside']],
  ['ai-mental-health','Mental-health signals','Consent before analysis','mental','Voice waveform entering a consented clinical review screen',['Voice biomarker with consent','Speech waveform and uncertainty','Clinician screening conversation']],
];

const palette = { ink:'#10251f', green:'#2f6b52', mint:'#94c9b2', cream:'#f4efe2', orange:'#e57b5f', blue:'#5a86a8', white:'#fffdf7' };
const esc = value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[ch]));

function baseIcon(kind) {
  const common = `stroke="${palette.cream}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none"`;
  const icons = {
    clinical:`<rect x="760" y="244" width="360" height="342" rx="24" ${common}/><path d="M808 470l62-68 70 45 78-116 61 36" ${common}/><circle cx="1018" cy="331" r="13" fill="${palette.orange}"/><path d="M660 316h72m-36-36v72" ${common}/>` ,
    liver:`<path d="M734 372c55-112 284-144 392-43 50 47 5 150-101 178-80 21-126 103-230 55-82-38-111-114-61-190z" fill="${palette.orange}" opacity=".92"/><circle cx="1015" cy="390" r="34" fill="none" stroke="${palette.cream}" stroke-width="10"/><path d="M1040 415l66 66" ${common}/>` ,
    document:`<rect x="770" y="230" width="330" height="370" rx="22" fill="${palette.white}" opacity=".96"/><path d="M830 330h210M830 404h210M830 478h130" stroke="${palette.green}" stroke-width="12"/><path d="M803 322l15 15 28-32M803 396l15 15 28-32M803 470l15 15 28-32" stroke="${palette.orange}" stroke-width="9" fill="none"/>`,
    molecule:`<g ${common}><circle cx="840" cy="350" r="58"/><circle cx="1030" cy="315" r="46"/><circle cx="1090" cy="490" r="64"/><circle cx="875" cy="525" r="42"/><path d="M895 338l89-15M1050 358l24 69M1033 498l-116 20M856 483l-3-75"/></g>`,
    mammogram:`<rect x="775" y="225" width="320" height="380" rx="20" fill="#1b3933" stroke="${palette.mint}" stroke-width="8"/><path d="M840 500c8-153 70-235 184-217 57 9 71 98 14 151-51 47-75 83-70 116" ${common}/><circle cx="997" cy="368" r="20" fill="${palette.orange}"/><path d="M742 640h392" ${common}/>`,
    supplement:`<path d="M800 520h260l-30 112H830z" fill="${palette.white}" opacity=".92"/><path d="M845 500c45-112 124-174 237-184" ${common}/><circle cx="1084" cy="312" r="40" fill="${palette.orange}"/><path d="M740 660h410" ${common}/>`,
    monitor:`<rect x="735" y="235" width="410" height="350" rx="28" fill="#173a32" stroke="${palette.mint}" stroke-width="8"/><path d="M780 430h80l40-95 60 175 55-130 42 50h52" ${common}/><circle cx="1090" cy="292" r="34" fill="${palette.orange}"/><path d="M1090 275v23m0 15v2" stroke="${palette.white}" stroke-width="8"/>`,
    muscle:`<g ${common}><path d="M760 420h80M1080 420h80M840 360v120M1080 360v120M880 395h160v50H880z"/><path d="M820 340h40v160h-40M1060 340h40v160h-40"/></g><path d="M820 580c100-88 205-88 300 0" stroke="${palette.orange}" stroke-width="16" fill="none"/>`,
    heart:`<path d="M950 560C710 425 760 270 875 282c53 6 75 42 78 70 4-28 31-66 84-70 115-9 159 145-87 278z" fill="${palette.orange}"/><path d="M720 640h120l44-86 70 130 60-104 55 60h100" ${common}/>`,
    vial:`<g><rect x="820" y="280" width="220" height="300" rx="28" fill="${palette.white}"/><rect x="850" y="220" width="160" height="78" rx="12" fill="${palette.blue}"/><rect x="848" y="388" width="164" height="90" rx="10" fill="${palette.orange}" opacity=".92"/><path d="M875 430h110" stroke="${palette.white}" stroke-width="10"/></g><path d="M1085 295l80 80m0-80l-80 80" stroke="${palette.orange}" stroke-width="16"/>`,
    screening:`<g fill="#173a32" stroke="${palette.mint}" stroke-width="6"><rect x="720" y="250" width="190" height="260" rx="16"/><rect x="940" y="250" width="190" height="260" rx="16"/></g><circle cx="1030" cy="370" r="30" fill="${palette.orange}"/><path d="M760 580h340" ${common}/><path d="M790 580v-54M880 580v-96M970 580v-132M1060 580v-76" stroke="${palette.orange}" stroke-width="24"/>`,
    protein:`<circle cx="930" cy="410" r="175" fill="${palette.white}" opacity=".95"/><circle cx="930" cy="410" r="110" fill="${palette.mint}"/><path d="M725 640h410M790 640v-70M900 640v-115M1010 640v-90M1120 640v-130" stroke="${palette.orange}" stroke-width="18"/>`,
    chat:`<path d="M730 265h320a35 35 0 0135 35v155a35 35 0 01-35 35H850l-90 70 20-70h-50a35 35 0 01-35-35V300a35 35 0 0135-35z" fill="${palette.white}"/><path d="M770 340h220M770 400h140" stroke="${palette.green}" stroke-width="13"/><circle cx="1090" cy="545" r="70" fill="${palette.orange}"/><path d="M1090 510v50m0 26v2" stroke="${palette.white}" stroke-width="12"/>`,
    radiology:`<g fill="#173a32" stroke="${palette.mint}" stroke-width="6"><rect x="700" y="250" width="220" height="300" rx="18"/><rect x="950" y="250" width="220" height="300" rx="18"/></g><path d="M810 310v180M760 350c30-30 70-30 100 0M760 430c30 30 70 30 100 0" ${common}/><circle cx="1060" cy="395" r="78" fill="none" stroke="${palette.cream}" stroke-width="10"/><circle cx="1095" cy="370" r="16" fill="${palette.orange}"/>`,
    caffeine:`<path d="M780 315h245v210a80 80 0 01-80 80h-85a80 80 0 01-80-80z" fill="${palette.white}"/><path d="M1025 365h45c100 0 100 140 0 140h-45" ${common}/><path d="M830 265c-32-55 28-72 0-122M920 265c-32-55 28-72 0-122" ${common}/><circle cx="1120" cy="570" r="78" fill="${palette.orange}"/><path d="M1120 520v54l34 24" ${common}/>`,
    sleep:`<path d="M1015 252c-110 35-155 172-80 263 48 58 134 72 200 30-31 78-108 133-199 133-124 0-225-101-225-225 0-111 80-203 185-222 41-7 82 1 119 21z" fill="${palette.cream}"/><path d="M1080 250l14 32 34 4-26 23 8 34-30-18-30 18 8-34-26-23 34-4z" fill="${palette.orange}"/>`,
    scale:`<rect x="760" y="230" width="330" height="390" rx="40" fill="${palette.white}"/><path d="M830 330a95 95 0 01200 0" stroke="${palette.green}" stroke-width="18" fill="none"/><path d="M930 330l65-52" stroke="${palette.orange}" stroke-width="12"/><path d="M820 510h220" stroke="${palette.mint}" stroke-width="28"/><path d="M820 555h135" stroke="${palette.orange}" stroke-width="28"/>`,
    peptide:`<g ${common}>${[0,1,2,3,4].map((i)=>`<circle cx="${760+i*95}" cy="${360+(i%2)*90}" r="38"/><path d="M${798+i*95} ${390+(i%2)*30}l57 ${i%2?-50:50}"/>`).join('')}</g><rect x="835" y="565" width="240" height="70" rx="12" fill="none" stroke="${palette.orange}" stroke-width="8"/><path d="M875 600h160" stroke="${palette.orange}" stroke-width="10"/>`,
    evidence:`<rect x="720" y="285" width="250" height="300" rx="18" fill="${palette.white}"/><rect x="920" y="235" width="250" height="300" rx="18" fill="${palette.mint}"/><path d="M765 360h150M765 420h150M965 310h150M965 370h150" stroke="${palette.green}" stroke-width="12"/><path d="M810 625l70-70 70 45 110-130" stroke="${palette.orange}" stroke-width="16" fill="none"/>`,
    hormone:`<rect x="735" y="265" width="160" height="300" rx="25" fill="${palette.white}"/><rect x="765" y="215" width="100" height="65" rx="10" fill="${palette.blue}"/><path d="M980 580V390h75v190M1090 580V300h75v280" fill="${palette.orange}"/><path d="M940 580h260" ${common}/><text x="1000" y="620" fill="${palette.cream}" font-size="28">strength</text>`,
    triage:`<path d="M720 320h340" stroke="${palette.cream}" stroke-width="30"/><path d="M720 420h250" stroke="${palette.mint}" stroke-width="30"/><path d="M720 520h180" stroke="${palette.blue}" stroke-width="30"/><circle cx="1110" cy="320" r="60" fill="${palette.orange}"/><path d="M1080 320l22 22 42-55" stroke="${palette.white}" stroke-width="12" fill="none"/>`,
    creatine:`<path d="M760 560h260l-35 105H795z" fill="${palette.white}"/><path d="M815 540c35-118 120-178 250-182" ${common}/><path d="M1090 245l-70 150h82l-55 140 155-190h-92l65-100z" fill="${palette.orange}"/>`,
    scribe:`<path d="M720 360c0-60 50-110 110-110s110 50 110 110-50 110-110 110-110-50-110-110z" fill="${palette.orange}"/><path d="M830 300v120M785 360h90" ${common}/><rect x="970" y="220" width="230" height="380" rx="20" fill="${palette.white}"/><path d="M1010 315h150M1010 380h150M1010 445h110" stroke="${palette.green}" stroke-width="11"/>`,
    carbs:`<ellipse cx="900" cy="460" rx="210" ry="135" fill="${palette.white}"/><ellipse cx="900" cy="450" rx="145" ry="85" fill="${palette.orange}"/><path d="M1110 620c25-130 70-230 120-300" stroke="${palette.mint}" stroke-width="22" fill="none"/><path d="M1170 340l60-20 10 64" ${common}/>`,
    bulk:`<path d="M720 600h450M770 600V300" ${common}/><path d="M790 550l105-30 100-80 110-38" stroke="${palette.orange}" stroke-width="18" fill="none"/><path d="M790 520l110-10 100-38 105-12" stroke="${palette.mint}" stroke-width="14" fill="none"/><circle cx="1105" cy="402" r="18" fill="${palette.orange}"/>`,
    robotic:`<path d="M785 230v145l105 75v150M1085 230v145l-105 75v150" ${common}/><circle cx="785" cy="230" r="42" fill="${palette.orange}"/><circle cx="1085" cy="230" r="42" fill="${palette.orange}"/><rect x="860" y="570" width="150" height="55" rx="18" fill="${palette.mint}"/><path d="M935 450v120" ${common}/>`,
    discovery:`<path d="M720 250h470l-175 210v145H895V460z" fill="${palette.mint}" opacity=".9"/><g fill="${palette.orange}"><circle cx="800" cy="310" r="28"/><circle cx="900" cy="300" r="18"/><circle cx="1020" cy="325" r="34"/><circle cx="1115" cy="295" r="22"/></g><rect x="870" y="620" width="170" height="55" rx="27" fill="${palette.white}"/>`,
    wearable:`<rect x="825" y="250" width="230" height="360" rx="55" fill="${palette.white}"/><rect x="860" y="315" width="160" height="220" rx="22" fill="#173a32"/><path d="M880 425h35l25-55 35 105 25-50h20" stroke="${palette.orange}" stroke-width="10" fill="none"/><path d="M880 200h120M880 660h120" ${common}/>`,
    llm:`<rect x="710" y="250" width="250" height="340" rx="22" fill="${palette.white}"/><rect x="980" y="250" width="210" height="340" rx="22" fill="${palette.mint}"/><path d="M755 330h160M755 390h160M755 450h120M1020 340h125M1020 405h125" stroke="${palette.green}" stroke-width="12"/><path d="M1030 505l35 35 75-85" stroke="${palette.orange}" stroke-width="16" fill="none"/>`,
    dna:`<path d="M790 230c230 120 230 310 0 430M1080 230c-230 120-230 310 0 430" ${common}/><path d="M845 270h180M810 350h250M810 520h250M845 610h180" stroke="${palette.mint}" stroke-width="10"/><path d="M915 390l70 70M985 390l-70 70" stroke="${palette.orange}" stroke-width="18"/>`,
    pathology:`<rect x="720" y="235" width="430" height="390" rx="20" fill="#f2d8d0"/><g fill="#985c79" opacity=".72">${[[780,310],[880,290],[1010,330],[1080,430],[820,470],[940,500],[1020,545]].map(([x,y])=>`<circle cx="${x}" cy="${y}" r="34"/>`).join('')}</g><circle cx="1010" cy="330" r="68" fill="none" stroke="${palette.orange}" stroke-width="12"/>`,
    implant:`<path d="M835 360c0-70 55-125 125-125s125 55 125 125v210H835z" fill="${palette.white}"/><circle cx="960" cy="360" r="45" fill="${palette.orange}"/><path d="M1100 320q100 40 0 80M1140 280q170 80 0 160" ${common}/><path d="M900 570v90" ${common}/>`,
    imaging:`<g fill="#173a32" stroke="${palette.mint}" stroke-width="6"><rect x="675" y="285" width="190" height="250" rx="18"/><rect x="885" y="285" width="190" height="250" rx="18"/><rect x="1095" y="285" width="190" height="250" rx="18"/></g><circle cx="770" cy="410" r="62" fill="none" stroke="${palette.cream}" stroke-width="10"/><path d="M940 470c20-105 55-140 80-75 15 38 10 80-15 120" ${common}/><path d="M1135 470l55-110 55 110" stroke="${palette.orange}" stroke-width="14" fill="none"/>`,
    mental:`<path d="M700 410h75l40-90 60 180 65-145 45 75h70" stroke="${palette.orange}" stroke-width="14" fill="none"/><rect x="1040" y="245" width="230" height="330" rx="22" fill="${palette.white}"/><path d="M1080 340h150M1080 405h110" stroke="${palette.green}" stroke-width="12"/><path d="M1090 505l35 35 75-85" stroke="${palette.orange}" stroke-width="16" fill="none"/>`
  };
  return icons[kind] || icons.evidence;
}

function svgFor(entry, width=1600, height=900, share=false) {
  const [slug,label,stat,kind] = entry;
  const words = label.split(' ');
  const labelLines = label.length > 21 ? words.reduce((lines, word) => {
    if (lines.length === 1 && `${lines[0]} ${word}`.trim().length <= Math.ceil(label.length / 2) + 3) lines[0] = `${lines[0]} ${word}`.trim();
    else if (lines.length === 1) lines.push(word);
    else lines[1] = `${lines[1]} ${word}`.trim();
    return lines;
  }, ['']) : [label];
  const safeLabel = labelLines.map(esc);
  const safeStat = esc(stat);
  const labelY = share ? 210 : 230;
  const statY = labelY + (safeLabel.length > 1 ? 142 : 92);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 1600 900" role="img" aria-labelledby="title desc">
  <title id="title">${safeLabel}</title><desc id="desc">The Med Frontier original medical graphic</desc>
  <rect width="1600" height="900" fill="${palette.ink}"/>
  <path d="M0 730C280 650 430 820 720 730s470-20 880-130v300H0z" fill="${palette.green}" opacity=".55"/>
  <g opacity=".10" stroke="${palette.mint}" stroke-width="2">${Array.from({length:14},(_,i)=>`<path d="M${i*125} 0v900"/>`).join('')}${Array.from({length:8},(_,i)=>`<path d="M0 ${i*125}h1600"/>`).join('')}</g>
  <rect x="90" y="88" width="300" height="42" rx="21" fill="${palette.orange}"/>
  <text x="120" y="117" fill="${palette.white}" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" letter-spacing="3">THE MED FRONTIER</text>
  <text x="90" y="${labelY}" fill="${palette.cream}" font-family="Georgia,serif" font-size="${share?58:62}" font-weight="700">${safeLabel.map((line,index)=>`<tspan x="90" dy="${index ? 68 : 0}">${line}</tspan>`).join('')}</text>
  <text x="94" y="${statY}" fill="${palette.mint}" font-family="Arial,Helvetica,sans-serif" font-size="32">${safeStat}</text>
  <g transform="translate(100 ${share?-70:0})">${baseIcon(kind)}</g>
  <text x="90" y="820" fill="${palette.cream}" opacity=".72" font-family="Arial,Helvetica,sans-serif" font-size="24">Research, evidence, and what I think it means.</text>
  <circle cx="1500" cy="98" r="28" fill="${palette.orange}"/><circle cx="1430" cy="98" r="12" fill="${palette.mint}"/>
  </svg>`;
}

async function buildImages() {
  const sharp = require('sharp');
  const root = process.cwd();
  const outDir = path.join(root, 'images');
  await fs.mkdir(outDir, { recursive: true });
  for (const entry of articles) {
    const [slug] = entry;
    const svg = svgFor(entry);
    await fs.writeFile(path.join(outDir, `${slug}-hero.svg`), svg);
    for (const width of [800,1200,1600]) {
      await sharp(Buffer.from(svg)).resize(width, Math.round(width * 9 / 16), { fit:'cover' }).webp({quality:82, effort:6}).toFile(path.join(outDir, `${slug}-${width}.webp`));
    }
    const shareSvg = svgFor(entry,1200,630,true);
    await sharp(Buffer.from(shareSvg)).resize(1200,630,{fit:'cover'}).webp({quality:84,effort:6}).toFile(path.join(outDir, `${slug}-share.webp`));
  }
  const home = ['home','The Med Frontier','Medical AI · training evidence','evidence'];
  await sharp(Buffer.from(svgFor(home,1200,630,true))).resize(1200,630,{fit:'cover'}).webp({quality:84,effort:6}).toFile(path.join(outDir,'the-med-frontier-share.webp'));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await buildImages();
