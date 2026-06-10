#!/usr/bin/env node
/* Bench gravar→transcrever na sb-011 (Preciso Me Encontrar — única melodia conferida):
 * sintetiza uma "performance" com os samples reais de trompete do app, transcreve com o
 * detector de produção + note-segmenter, e mede contra o gabarito — e contra o OMR cru.
 *
 * Uso: node tools/transcricao/bench_sb011.mjs   (escreve out/*.wav e out/result.json)
 */
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { chromium } from '@playwright/test';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.abc': 'text/plain', '.mp3': 'audio/mpeg', '.css': 'text/css' };

function serve() {
  return new Promise((ok) => {
    const srv = http.createServer((req, res) => {
      const p = path.join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname));
      if (!p.startsWith(ROOT) || !fs.existsSync(p) || !fs.statSync(p).isFile()) { res.writeHead(404); return res.end(); }
      res.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream', 'access-control-allow-origin': '*' });
      fs.createReadStream(p).pipe(res);
    }).listen(0, '127.0.0.1', () => ok(srv));
  });
}

/* métricas: casamento por (mesmo midi, |Δcélula| ≤ tol) com dois ponteiros; melodia por
 * distância de edição na sequência de alturas (independente de ritmo). */
function casa(gt, tr, tol = 1) {
  const used = new Set();
  let matched = 0, durOk = 0, octErr = 0, pcOk = 0;
  for (const g of gt) {
    let best = -1, bestD = 1e9;
    tr.forEach((t, i) => {
      if (used.has(i) || t.midi !== g.midi) return;
      const d = Math.abs(t.cell - g.cell);
      if (d <= tol && d < bestD) { best = i; bestD = d; }
    });
    if (best >= 0) {
      used.add(best); matched++;
      if (Math.abs(tr[best].durCells - g.durCells) <= 1) durOk++;
    }
  }
  for (const g of gt) {                       // diagnóstico: classe certa em oitava errada?
    if (tr.some((t) => t.midi !== g.midi && t.midi % 12 === g.midi % 12 && Math.abs(t.cell - g.cell) <= tol && Math.abs(t.midi - g.midi) % 12 === 0)) octErr++;
    if (tr.some((t) => t.midi % 12 === g.midi % 12 && Math.abs(t.cell - g.cell) <= tol)) pcOk++;
  }
  return { matched, durOk, octErr, pcOk, precision: matched / (tr.length || 1), recall: matched / (gt.length || 1) };
}
function editDist(a, b) {
  const D = Array.from({ length: a.length + 1 }, (_, i) => [i, ...Array(b.length).fill(0)]);
  for (let j = 0; j <= b.length; j++) D[0][j] = j;
  for (let i = 1; i <= a.length; i++)
    for (let j = 1; j <= b.length; j++)
      D[i][j] = Math.min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return D[a.length][b.length];
}
const melodia = (gt, tr) => 1 - editDist(gt.map((e) => e.midi), tr.map((e) => e.midi)) / gt.length;

const NOME = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];
const nm = (m) => NOME[m % 12] + (Math.floor(m / 12) - 1);
const linha = (evs) => evs.map((e) => `${nm(e.midi)}×${e.durCells}@${e.cell}`).join(' ');

const srv = await serve();
const port = srv.address().port;
const browser = await chromium.launch();
const page = await browser.newPage();
page.on('pageerror', (e) => console.error('pageerror:', e.message));
await page.goto(`http://127.0.0.1:${port}/tools/transcricao/bench.html`);

const res = await page.evaluate((cfg) => runBench(cfg), {
  profiles: {
    limpo: { detuneCents: 7, jitterMs: 12, gapMs: 28, velJitterDb: 2, t0: 0.15, seed: 1 },
    sujo: { detuneCents: 18, jitterMs: 25, gapMs: 22, velJitterDb: 4, snrDb: 22, t0: 0.15, seed: 7 },
  },
});
await browser.close();
srv.close();

const { gt, omr } = res;
if (gt.violations.length) { console.error('GABARITO inválido:', gt.violations); process.exit(1); }
console.log(`gabarito: ${gt.events.length} notas, ${gt.totalCells} células, ${gt.bpm}bpm`);
console.log('  ' + linha(gt.events));

const outDir = path.join(ROOT, 'tools/transcricao/out');
fs.mkdirSync(outDir, { recursive: true });
const tabela = [];
for (const [name, p] of Object.entries(res.profiles)) {
  fs.writeFileSync(path.join(outDir, `sb-011-${name}.wav`), Buffer.from(p.wav, 'base64'));
  const m = casa(gt.events, p.events);
  tabela.push({
    fonte: `áudio (${name})`, notas: p.events.length,
    'nota+ritmo': `${m.matched}/${gt.events.length}`,
    'duração ok': `${m.durOk}/${m.matched}`,
    'melodia %': Math.round(melodia(gt.events, p.events) * 100),
    extras: `afinação detectada ${p.tuningOffsetCents}c · latência ${p.shiftMs}ms`,
  });
  console.log(`\n${name}: ${p.nRaw} notas segmentadas → ${p.events.length} quantizadas`);
  console.log('  ' + linha(p.events));
}
const omrJanela = omr.events.filter((e) => e.cell < gt.totalCells);
const mo = casa(gt.events, omrJanela);
tabela.push({
  fonte: 'OMR cru', notas: omrJanela.length,
  'nota+ritmo': `${mo.matched}/${gt.events.length}`,
  'duração ok': `${mo.durOk}/${mo.matched}`,
  'melodia %': Math.round(melodia(gt.events, omrJanela) * 100),
  extras: `${omr.violations.length} compassos com soma errada na página toda`,
});
console.log('\nOMR cru (janela do gabarito):\n  ' + linha(omrJanela));
console.table(tabela);
fs.writeFileSync(path.join(outDir, 'result.json'), JSON.stringify({ ...res, profiles: Object.fromEntries(Object.entries(res.profiles).map(([k, v]) => [k, { ...v, wav: undefined }])) }, null, 1));
console.log(`wavs e result.json em tools/transcricao/out/`);
