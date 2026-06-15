'use strict';
// Sambrass Tutor — PWA (vanilla). Lê ./data/*.json gerados de content/.

const DB = {};            // dados carregados
const $ = (s, e = document) => e.querySelector(s);
const tela = document.getElementById('tela');

async function carregar() {
  const get = async (f) => { try { return await (await fetch('./data/' + f)).json(); } catch { return null; } };
  [DB.pieces, DB.curriculo, DB.trilha, DB.cells, DB.rotina, DB.quality, DB.escada, DB.percurso, DB.lotes] = await Promise.all(
    ['pieces.json', 'curriculum.json', 'trilha.json', 'cells.json', 'rotina.json', 'quality.json', 'escada.json', 'percurso.json', 'lotes.json'].map(get));
  DB.byNum = {}; (DB.pieces?.pieces || []).forEach(p => DB.byNum[p.num] = p);
  DB.nivelByNum = {}; (DB.escada?.pieces || []).forEach(e => DB.nivelByNum[e.num] = e.nivel_minimo);
  DB.percByNum = {}; (DB.percurso || []).forEach(m => DB.percByNum[m.num] = m);
}

/* ---------- progresso (localStorage) ---------- */
const PROG = JSON.parse(localStorage.getItem('sambrass_prog') || '{}');
const setProg = (n, s) => { if (PROG[n] === s) delete PROG[n]; else PROG[n] = s; localStorage.setItem('sambrass_prog', JSON.stringify(PROG)); };

/* progresso SDT (autoavaliação 1–5, sem XP/cadeado) — rota "O Caminho do Sambrass".
   Fonte de verdade = sb2_logs {num:[{d,n}]}; dominada = melhor nível ≥ 4. */
const store = {
  get(k, d) { try { const v = JSON.parse(localStorage.getItem('sb2_' + k)); return v == null ? d : v; } catch { return d; } },
  set(k, v) { try { localStorage.setItem('sb2_' + k, JSON.stringify(v)); } catch {} }
};
const RATELBL = ['', 'tive dificuldade na leitura', 'leio, mas paro/erro', 'toco seguido, lento', 'toco no andamento', 'toco de cor 🎉'];
const LCOR = ['', '#2e6b4f', '#5a7a1f', '#8a5a1f', '#a3431f', '#7a1f1f', '#3a3a3a'];   // cor por lote 1–6
const bestLevel = n => { const l = store.get('logs', {})[n]; return (!l || !l.length) ? 0 : Math.max(...l.map(x => x.n)); };
const isDone = n => bestLevel(n) >= 4;
const countDone = () => (DB.percurso || []).filter(m => isDone(m.num)).length;
const prepDone = () => store.get('prepdone', false);
const markDay = () => { const days = store.get('days', []); const t = new Date().toISOString().slice(0, 10); if (!days.includes(t)) { days.push(t); store.set('days', days); } };
const streakCount = () => { const days = store.get('days', []).slice().sort(); let s = 0, d = new Date(); for (; ;) { const k = d.toISOString().slice(0, 10); if (days.includes(k)) { s++; d.setDate(d.getDate() - 1); } else break; } return s; };
// migração única: 'dominada' do modelo antigo (sambrass_prog) vira um log nível 4
(function migrarProg() {
  if (store.get('migrado', false)) return;
  const logs = store.get('logs', {}), hoje = new Date().toISOString().slice(0, 10);
  Object.keys(PROG).forEach(n => { if (PROG[n] === 'dominada' && !(logs[n] || []).some(x => x.n >= 4)) (logs[n] = logs[n] || []).push({ d: hoje, n: 4 }); });
  store.set('logs', logs); store.set('migrado', true);
})();
const TOM = { C: 'Dó', G: 'Sol', D: 'Ré', A: 'Lá', E: 'Mi', 'F#': 'Fá#', F: 'Fá', Bb: 'Si♭', Eb: 'Mi♭', Ab: 'Lá♭', Db: 'Ré♭', B: 'Si' };
const WRIT = { C: 'D', G: 'A', D: 'E', A: 'B', E: 'F#', 'F#': 'G#', F: 'G', Bb: 'C', Eb: 'F', Ab: 'Bb', Db: 'Eb', B: 'C#' };
const tomEscrito = p => (WRIT[p.key_concert] || p.key_concert) + (p.modulates_to_concert ? '→' + (WRIT[p.modulates_to_concert] || '') : '');
// qualidade da melodia: rascunho (OMR) < dedos (fusão pela digitação) < conferida (à mão)
const QUAL = {
  conferida: { tag: '✓', cls: 'q-ok', txt: 'conferida à mão' },
  dedos: { tag: '♪', cls: 'q-mid', txt: 'tom pelos dedos · oitava/ritmo provisórios' },
  rascunho: { tag: '~', cls: 'q-raw', txt: 'leitura automática (OMR) · em revisão' }
};
const idOf = n => 'sb-' + String(n).padStart(3, '0');
const qualOf = n => (DB.quality && DB.quality[idOf(n)]) || 'rascunho';
// nível pedagógico (escada Book1/2/Arban)
const NIVEL = { book1: 'Book 1', book2: 'Book 2', arban: 'Arban' };
const nivelOf = n => (DB.nivelByNum && DB.nivelByNum[n]) || null;
const NIVEL_FULL = { book1: 'Book 1 · fundação', book2: 'Book 2 · células e tons novos', arban: 'Arban · topo técnico' };
const NIVEL_DESC = {
  book1: 'A base do caderno: som, tons naturais (Dó/Fá/Sol/Sib escritos), colcheias em grupo, contratempo e anacruse. Esgote este nível antes de subir.',
  book2: 'Células novas — semicolcheia, tercina, colcheia pontuada — e armaduras com mais acidentes (Ré/Lá/Mib).',
  arban: 'O topo técnico: ornamentos, staccato duplo (tu-ku), arpejo de 7ª da dominante e resistência de forma longa.'
};
// nível da ARMADURA ESCRITA na escada (espelha content/curadoria/lib.py KEY_LEVEL)
const KEY_LEVEL = { C: 1, F: 1, G: 1, Bb: 1, D: 2, A: 2, Eb: 2, E: 2, Db: 2, Ab: 2, 'F#': 3, B: 3 };
const LVLKEY = { 1: 'book1', 2: 'book2', 3: 'arban' };
const keyLevelOf = concert => KEY_LEVEL[WRIT[concert] || concert] || 2;
// célula/arpejo → nível em que se destrava (para o Vocabulário)
const CELL_LEVEL = { C1: 'book1', C2: 'book1', C6: 'book1', C7: 'book1', C3: 'book2', C4: 'book2', C5: 'book2', A1: 'book1', A2: 'book1', A4: 'book1', A3: 'arban' };
// competências exigidas por uma peça (espelha lib.py piece_skills) — usado no Banco e no Vocabulário
function pieceTags(p) {
  const t = new Set(), cel = new Set(p.celulas || []), rq = (p.requisitos || []).join(' '), forma = p.forma || [];
  if (cel.has('C2') || rq.includes('síncope')) t.add('sincope');
  if (cel.has('C6') || rq.includes('contratempo')) t.add('contratempo');
  if (cel.has('C5') || rq.includes('tercina')) t.add('tercina');
  if (cel.has('C4') || rq.includes('semicolcheia')) t.add('semicolcheia');
  if (cel.has('C3') || rq.includes('pontuada')) t.add('pontuada');
  if (cel.has('C7') || rq.includes('anacruse')) t.add('anacruse');
  if (rq.includes('cromatismo')) t.add('cromatismo');
  if (rq.includes('casas')) t.add('casas');
  if (rq.includes('DS') || rq.includes('DC')) t.add('ds-dc');
  if (p.modulates_to_concert || rq.includes('modula')) t.add('modulacao');
  if (rq.includes('ornamento')) t.add('ornamentos');
  if (p.compasso === '4/4') t.add('quatro');
  if (rq.includes('extensa') || forma.length >= 4) t.add('forma-extensa');
  else if (forma.length >= 3) t.add('forma-longa');
  return t;
}
const COMP_CHIPS = [['sincope', 'síncope'], ['contratempo', 'contratempo'], ['tercina', 'tercina'],
  ['semicolcheia', 'semicolcheia'], ['pontuada', 'colcheia pontuada'], ['anacruse', 'anacruse'],
  ['cromatismo', 'cromatismo'], ['casas', 'casas 1ª/2ª'], ['ds-dc', 'saltos D.S./D.C.'],
  ['modulacao', 'modulação'], ['forma-longa', 'forma longa'], ['forma-extensa', 'forma extensa'],
  ['ornamentos', 'ornamentos'], ['quatro', 'compasso 4/4']];
const EFF_CHIPS = [['agudo', 'agudo +'], ['vel', 'veloz +'], ['folego', 'fôlego +']];
const COMP_SHORT = { sincope: 'síncope', contratempo: 'contratempo', tercina: 'tercina', semicolcheia: 'semicolcheia', pontuada: 'pontuada', anacruse: 'anacruse', cromatismo: 'cromatismo', casas: 'casas', 'ds-dc': 'D.S./D.C.', modulacao: 'modulação', 'forma-longa': 'forma longa', 'forma-extensa': 'forma extensa' };
const COMP_SALIENT = ['tercina', 'semicolcheia', 'cromatismo', 'modulacao', 'contratempo', 'sincope', 'pontuada', 'anacruse', 'casas', 'ds-dc', 'forma-extensa', 'forma-longa'];
const difColor = d => { const t = Math.max(0, Math.min(1, ((d || 5) - 3) / 4)); return `hsl(${Math.round(130 * (1 - t))} 58% 42%)`; };

/* ---------- telas ---------- */
// A home é a Trilha (telaTrilha em trilha.js) — o caminho sugerido estilo Duolingo.

function linhaPeca(n) {
  const p = DB.byNum[n]; if (!p) return '';
  const m = DB.percByNum[n] || {}, q = QUAL[qualOf(n)], nv = nivelOf(n), done = isDone(n), dif = p.dificuldade || 0;
  const tg = pieceTags(p);
  const comp = COMP_SALIENT.filter(k => tg.has(k)).slice(0, 2).map(k => `<span class="ctag">${COMP_SHORT[k]}</span>`).join('');
  const fp = ['agudo', 'vel', 'folego'].map((k, i) => `<i class="fp${i}" style="height:${3 + (m[k] || 0) * 2}px"></i>`).join('');
  return `<li><div class="linha${done ? ' feita' : ''}">
      <button class="playmini" onclick="event.stopPropagation();tocarPeca(${n})" aria-label="tocar">▶</button>
      <a class="peca" href="#" onclick="verPeca(${n});return false">
        <div class="ptop"><span class="num">${String(n).padStart(3, '0')}</span> <span class="ptit">${p.titulo}</span> <span class="qual ${q.cls}" title="melodia: ${q.txt}">${q.tag}</span>${done ? ' <span class="feitatag">dominada ✓</span>' : ''}</div>
        <div class="pcomp">${p.compositor}</div>
        <div class="pchips"><span class="chip-tom">${TOM[p.key_concert] || p.key_concert}</span><span class="chip-c">${p.compasso}</span>${nv ? `<span class="niv niv-${nv}">${NIVEL[nv]}</span>` : ''}${comp}<span class="fp" title="esforço · agudo/veloz/fôlego">${fp}</span></div>
      </a>
      <div class="difb" style="background:${difColor(dif)}" title="dificuldade ${dif}/7">${dif || '?'}</div>
    </div></li>`;
}

// Banco = navegador por competências: combine nível (escada) · habilidade · esforço · busca.
function telaBanco() {
  const ps = (DB.pieces?.pieces || []).slice().sort((a, b) => (a.dificuldade || 0) - (b.dificuldade || 0) || a.num - b.num);
  const inp = 'width:100%;min-height:44px;padding:8px 12px;border:1px solid var(--linha);border-radius:8px;font:inherit;margin-bottom:6px';
  const cnt = {}; COMP_CHIPS.forEach(([k]) => cnt[k] = 0); const eff = { agudo: 0, vel: 0, folego: 0 };
  ps.forEach(p => {
    const tg = pieceTags(p); COMP_CHIPS.forEach(([k]) => { if (tg.has(k)) cnt[k]++; });
    const m = DB.percByNum[p.num] || {}; ['agudo', 'vel', 'folego'].forEach(k => { if ((m[k] || 0) >= 4) eff[k]++; });
  });
  const chip = (kind, k, lab, n) => n ? `<button class="chip ${kind}" data-kind="${kind}" data-k="${k}">${lab} <span class="chipn">${n}</span></button>` : '';
  tela.innerHTML = `<h2 class="sec">Banco — ${ps.length} peças</h2>
    <p class="meta">Navegue por <b>competência</b>: combine nível, habilidade e esforço (e busque pelo nome). Ordenadas da <b>mais fácil à mais difícil</b> — a numeração do caderno é mantida.</p>
    <input id="busca" placeholder="buscar título ou compositor…" style="${inp}">
    <select id="fnivel" style="${inp}">
      <option value="">todos os níveis (escada pedagógica)</option>
      <option value="book1">Book 1 — fundação</option>
      <option value="book2">Book 2 — células/tons novos</option>
      <option value="arban">Arban — ornamento/resistência</option></select>
    <div class="chiprow">${COMP_CHIPS.map(([k, l]) => chip('comp', k, l, cnt[k])).join('')}</div>
    <div class="chiprow"><span class="chiplab">esforço:</span>${EFF_CHIPS.map(([k, l]) => chip('eff', k, l, eff[k])).join('')}</div>
    <div class="bancohead"><span class="meta" id="bancocount"></span><button class="limpaf" id="limpaf" hidden>limpar ✕</button></div>
    <ul class="lista" id="listapecas"></ul>`;
  const act = { comp: new Set(), eff: new Set() };
  const aplica = () => {
    const q = ($('#busca').value || '').toLowerCase(), nv = $('#fnivel').value;
    const out = ps.filter(p => {
      if (!(p.titulo + ' ' + p.compositor).toLowerCase().includes(q)) return false;
      if (nv && nivelOf(p.num) !== nv) return false;
      const tg = pieceTags(p); for (const k of act.comp) if (!tg.has(k)) return false;
      const m = DB.percByNum[p.num] || {}; for (const k of act.eff) if ((m[k] || 0) < 4) return false;
      return true;
    });
    $('#listapecas').innerHTML = out.map(p => linhaPeca(p.num)).join('') || '<li class="meta" style="padding:12px">nenhuma peça nesse filtro.</li>';
    $('#bancocount').textContent = `${out.length} de ${ps.length} peças`;
    $('#limpaf').hidden = !(act.comp.size || act.eff.size || nv);
  };
  $('#busca').oninput = aplica; $('#fnivel').onchange = aplica;
  tela.querySelectorAll('.chip').forEach(b => b.onclick = () => {
    const set = b.dataset.kind === 'comp' ? act.comp : act.eff, k = b.dataset.k;
    if (set.has(k)) { set.delete(k); b.classList.remove('on'); } else { set.add(k); b.classList.add('on'); }
    aplica();
  });
  $('#limpaf').onclick = () => { act.comp.clear(); act.eff.clear(); $('#fnivel').value = ''; tela.querySelectorAll('.chip.on').forEach(b => b.classList.remove('on')); aplica(); };
  aplica();
}

function verPeca(n) {
  const p = DB.byNum[n]; if (!p) return;
  const lvl = bestLevel(n), nv = nivelOf(n);
  const status = isDone(n)
    ? `<span class="niv niv-book1">dominada ✓</span> <span class="meta">autoavaliação ${lvl}/5</span>`
    : lvl ? `<span class="meta">em progresso — melhor: ${RATELBL[lvl]}</span>`
      : `<span class="meta">ainda não tocada</span>`;
  tela.innerHTML = `<button class="voltar" onclick="ir('banco')">‹ banco</button>
    <div class="card"><span class="dif">dif ${p.dificuldade || '?'}</span>
      <h3>${String(n).padStart(3, '0')} — ${p.titulo}</h3>
      <div class="meta">${p.compositor}</div>
      <div class="meta" style="margin:6px 0">Tom escrito <b>${tomEscrito(p)}</b> (concerto ${TOM[p.key_concert] || p.key_concert}) · ${p.compasso} · ${p.densidade} · forma ${(p.forma || []).join('/') || '?'}${nv ? ` · <span class="niv niv-${nv}">${NIVEL[nv]}</span>` : ''}</div>
      <div>${(p.celulas || []).map(c => `<span class="tag">${c}</span>`).join('')} ${(p.requisitos || []).map(r => `<span class="tag">${r}</span>`).join('')}</div>
      <div style="margin:10px 0"><b>Progresso:</b> ${status}</div>
      <div class="btnrow" style="justify-content:flex-start;margin-top:12px;gap:8px">
        <button class="acao" onclick="openMusic(${n})">abrir o plano (Story)</button>
        <a class="acao" href="./estudo.html?id=sb-${String(n).padStart(3, '0')}">🎤 tocar no tutor</a></div>
      <p class="meta" style="margin-top:8px">Vira <b>dominada ✓</b> (na trilha também) quando você se autoavalia nível 4+ no diário da Story.</p>
      ${p.obs ? `<p class="meta" style="font-style:italic;margin-top:10px">${p.obs}</p>` : ''}
    </div>`;
  window.scrollTo(0, 0);
}

function telaVocab() {
  const c = DB.cells || {}, pieces = (DB.pieces?.pieces || []), tot = pieces.length;
  const lvlTag = id => { const l = CELL_LEVEL[id]; return l ? ` <span class="niv niv-${l}">${NIVEL[l]}</span>` : ''; };
  const li = (arr, play) => (arr || []).map(x =>
    `<li>${play ? `<button class="prog" style="min-width:34px" onclick="tocarCell('${x.id}')">▶</button> ` : ''}<code>${x.id}</code> ${x.nome}${x.descricao ? ' — ' + x.descricao : ''}${lvlTag(x.id)}</li>`).join('');
  // tonalidades por nível da escada (pela armadura escrita), nomeadas em concerto
  const tk = { book1: {}, book2: {}, arban: {} };
  pieces.forEach(p => { const lk = LVLKEY[keyLevelOf(p.key_concert)], nm = TOM[p.key_concert] || p.key_concert; tk[lk][nm] = (tk[lk][nm] || 0) + 1; });
  const tomRow = lk => { const e = Object.entries(tk[lk]).sort((a, b) => b[1] - a[1]); return e.length ? e.map(([nm, n]) => `<span class="tag">${nm} <b>${n}</b></span>`).join(' ') : '<span class="meta">—</span>'; };
  // demais competências (contagens reais)
  const cnt = {}; COMP_CHIPS.forEach(([k]) => cnt[k] = 0);
  pieces.forEach(p => { const tg = pieceTags(p); COMP_CHIPS.forEach(([k]) => { if (tg.has(k)) cnt[k]++; }); });
  const comp = COMP_CHIPS.filter(([k]) => cnt[k]).map(([k, lab]) => `<span class="tag">${lab} <b>${cnt[k]}</b></span>`).join(' ');
  const c44 = pieces.filter(p => p.compasso === '4/4').length, c24 = tot - c44;
  tela.innerHTML = `<div class="card" style="text-align:center"><button class="acao" style="width:100%" onclick="openPrep()">🌬️ Aquecimento — 12 exercícios${prepDone() ? ' ✓' : ''}</button>
      <p class="meta" style="margin-top:8px">Prepare o corpo antes de tocar: ar → bocal → som → registro → articulação.</p></div>
    <h2 class="sec">Vocabulário do caderno</h2>
    <p class="meta">As competências das ${tot} peças, organizadas pela <b>escada</b> (Book 1 → Book 2 → Arban). Toque ▶ para ouvir cada célula.</p>
    <div class="card vocab"><h3>Células rítmicas</h3><ul class="lista">${li(c.celulas_ritmicas, true)}</ul></div>
    <div class="card vocab"><h3>Arpejos</h3><ul class="lista">${li(c.arpejos, false)}</ul></div>
    <div class="card vocab"><h3>Tonalidades <span class="meta">(pela armadura escrita)</span></h3>
      <div class="vocablvl"><span class="niv niv-book1">${NIVEL.book1}</span> ${tomRow('book1')}</div>
      <div class="vocablvl"><span class="niv niv-book2">${NIVEL.book2}</span> ${tomRow('book2')}</div>
      <div class="vocablvl"><span class="niv niv-arban">${NIVEL.arban}</span> ${tomRow('arban')}</div>
      <p class="meta" style="margin-top:8px">No trompete Bb a armadura escrita = tom de concerto + 2 semitons — por isso Dó de concerto se lê em Ré (2♯, Book 2), e só Sib/Fá/Sol/Dó escritos ficam no Book 1.</p></div>
    <div class="card vocab"><h3>Articulação, forma e leitura</h3><p class="tags">${comp || '<span class="meta">—</span>'}</p></div>
    <p class="meta">${c24} peças em 2/4 e ${c44} em 4/4. Dominar este vocabulário é ler o caderno à primeira vista.</p>`;
}

/* ---------- metrônomo (Web Audio) ---------- */
const M = { ctx: null, on: false, bpm: 100, alvo: 160, rampa: false, beats: 2, beat: 0, next: 0, bars: 0, timer: null };
function metroTela() {
  tela.innerHTML = `<h2 class="sec">Metrônomo</h2><div class="card metro">
    <div class="bpm"><span id="vbpm">${M.bpm}</span> <small>BPM</small></div>
    <input type="range" min="40" max="260" value="${M.bpm}" id="sbpm">
    <div class="beats" id="vbeats"></div>
    <div class="btnrow" style="margin:8px 0">
      <button class="toggle" id="tcomp">2/4</button>
      <button class="toggle ${M.rampa ? 'on' : ''}" id="trampa">rampa → <span id="valvo">${M.alvo}</span></button>
    </div>
    <input type="range" min="60" max="260" value="${M.alvo}" id="salvo" ${M.rampa ? '' : 'disabled'}>
    <div class="btnrow"><button class="acao ${M.on ? 'parar' : ''}" id="bgo">${M.on ? 'parar' : 'iniciar'}</button>
      <button class="toggle" id="btap">tap</button></div>
    <p class="meta" style="margin-top:10px">A rampa sobe 4 BPM a cada 4 compassos até o alvo — pratique a célula lenta e acelere.</p></div>`;
  desenhaBeats();
  $('#sbpm').oninput = e => { M.bpm = +e.target.value; $('#vbpm').textContent = M.bpm; };
  $('#salvo').oninput = e => { M.alvo = +e.target.value; $('#valvo').textContent = M.alvo; };
  $('#tcomp').onclick = e => { M.beats = M.beats === 2 ? 4 : (M.beats === 4 ? 3 : 2); e.target.textContent = M.beats + '/4'; desenhaBeats(); };
  $('#trampa').onclick = e => { M.rampa = !M.rampa; e.target.classList.toggle('on', M.rampa); $('#salvo').disabled = !M.rampa; };
  $('#bgo').onclick = toggleMetro;
  let taps = [];
  $('#btap').onclick = () => { const t = performance.now(); taps = taps.filter(x => t - x < 2000); taps.push(t); if (taps.length > 1) { const d = (taps[taps.length - 1] - taps[0]) / (taps.length - 1); M.bpm = Math.max(40, Math.min(260, Math.round(60000 / d))); $('#vbpm').textContent = M.bpm; $('#sbpm').value = M.bpm; } };
}
function desenhaBeats() { const v = $('#vbeats'); if (v) v.innerHTML = Array.from({ length: M.beats }, (_, i) => `<span class="beat" id="b${i}"></span>`).join(''); }
function toggleMetro() { M.on ? pararMetro() : iniciarMetro(); }
function iniciarMetro() {
  M.ctx = M.ctx || new (window.AudioContext || window.webkitAudioContext)();
  M.ctx.resume(); M.on = true; M.beat = 0; M.bars = 0; M.next = M.ctx.currentTime + 0.1;
  M.timer = setInterval(scheduler, 25);
  const b = $('#bgo'); if (b) { b.textContent = 'parar'; b.classList.add('parar'); }
}
function pararMetro() { M.on = false; clearInterval(M.timer); const b = $('#bgo'); if (b) { b.textContent = 'iniciar'; b.classList.remove('parar'); } }
function scheduler() {
  while (M.next < M.ctx.currentTime + 0.1) {
    click(M.next, M.beat === 0);
    flash(M.beat);
    M.next += 60 / M.bpm;
    M.beat = (M.beat + 1) % M.beats;
    if (M.beat === 0) { M.bars++; if (M.rampa && M.bars % 4 === 0 && M.bpm < M.alvo) { M.bpm = Math.min(M.alvo, M.bpm + 4); const v = $('#vbpm'); if (v) { v.textContent = M.bpm; $('#sbpm').value = M.bpm; } } }
  }
}
function click(t, acc) {
  const o = M.ctx.createOscillator(), g = M.ctx.createGain();
  o.frequency.value = acc ? 1500 : 900; g.gain.value = acc ? 0.5 : 0.3;
  o.connect(g); g.connect(M.ctx.destination);
  o.start(t); g.gain.exponentialRampToValueAtTime(0.001, t + 0.04); o.stop(t + 0.05);
}
function flash(i) { const at = M.next - M.ctx.currentTime; setTimeout(() => { document.querySelectorAll('.beat').forEach((b, j) => b.classList.toggle('on', j === i)); }, Math.max(0, at * 1000)); }

/* ---------- player (abcjs: partitura + MIDI trompete + cursor) ---------- */
let SYNTH = null, PLAYER = null;  // PLAYER = {abc, transpose, titulo, voltar}
async function loadAbc() { if (!DB.abc) DB.abc = await fetch('./data/abc.json').then(r => r.json()).catch(() => ({})); }
function pararSynth() { if (SYNTH) { try { SYNTH.pause(); } catch {} SYNTH = null; } }
// Áudio do celular: 1 AudioContext registrado no abcjs, retomado a cada toque (gesto).
let AC = null;
function audioUnlock() { try { if (!AC) { AC = new (window.AudioContext || window.webkitAudioContext)(); if (window.ABCJS?.synth?.registerAudioContext) ABCJS.synth.registerAudioContext(AC); } if (AC.state === 'suspended') AC.resume(); } catch (e) {} }
['pointerdown', 'touchend'].forEach(ev => document.addEventListener(ev, audioUnlock, { capture: true }));

async function abrirPlayer(id, titulo, prov, voltar) {
  pararMetro(); await loadAbc();
  const abc = (DB.abc || {})[id];
  PLAYER = abc ? { abc, transpose: 0, titulo, voltar: voltar || 'banco' } : null;
  document.querySelectorAll('.abas button').forEach(b => b.classList.remove('ativa'));
  if (!abc) { tela.innerHTML = `<button class="voltar" onclick="ir('${voltar || 'banco'}')">‹ voltar</button><p class="carregando">partitura não disponível.</p>`; return; }
  tela.innerHTML = `<button class="voltar" onclick="ir('${voltar || 'banco'}')">‹ voltar</button>
    <div class="card">
      <h3>${titulo}</h3>
      ${(() => { const t = (DB.quality && DB.quality[id]) || 'rascunho'; if (t === 'conferida') return ''; const m = QUAL[t]; return `<p class="meta">⚠ melodia provisória — ${m.txt}; as células são exatas</p>`; })()}
      <div class="btnrow" style="justify-content:flex-start;margin:4px 0 10px">
        <button class="toggle" id="tconcert">ouvir em concerto</button>
      </div>
      <div id="paper" class="paper"></div>
      <div id="audio" class="audio"></div>
      <p class="meta" style="margin-top:8px">▶ toca com timbre de trompete · ↔ controla o andamento · o cursor segue as notas.</p>
    </div>`;
  $('#tconcert').onclick = e => { const c = e.target.classList.toggle('on'); e.target.textContent = c ? 'ouvir escrito (Bb)' : 'ouvir em concerto'; renderPlayer(c ? -2 : 0); };
  renderPlayer(0);
  window.scrollTo(0, 0);
}

function renderPlayer(transpose) {
  if (!PLAYER) return;
  pararSynth(); PLAYER.transpose = transpose;
  let visual;
  try {
    visual = ABCJS.renderAbc('paper', PLAYER.abc, { add_classes: true, responsive: 'resize', visualTranspose: transpose })[0];
  } catch (e) { $('#paper').innerHTML = '<p class="meta">não consegui desenhar a partitura.</p>'; return; }
  if (!window.ABCJS || !ABCJS.synth || !ABCJS.synth.supportsAudio()) { $('#audio').innerHTML = '<p class="meta">áudio não suportado neste navegador.</p>'; return; }
  audioUnlock();
  try {
    SYNTH = new ABCJS.synth.SynthController();
    SYNTH.load('#audio', cursorCtl(), { displayPlay: true, displayProgress: true, displayWarp: true, displayLoop: true, displayRestart: true });
    SYNTH.setTune(visual, false, { program: 56, soundFontUrl: './vendor/soundfont/' })
      .catch(e => { const a = $('#audio'); if (a) a.insertAdjacentHTML('beforeend', `<p class="meta">não consegui carregar o som (${e}). Recarregue.</p>`); });
  } catch (e) { $('#audio').innerHTML = `<p class="meta">erro no player: ${e.message}</p>`; }
}
function cursorCtl() {
  const clear = () => document.querySelectorAll('.abcjs-highlight').forEach(el => el.classList.remove('abcjs-highlight'));
  return { onStart() {}, onFinished() { clear(); }, onEvent(ev) { if (!ev || ev.measureStart && ev.left === null) return; clear(); (ev.elements || []).forEach(s => s.forEach(el => el.classList.add('abcjs-highlight'))); } };
}
window.abrirPlayer = abrirPlayer;
window.tocarPeca = n => { const p = DB.byNum[n]; if (p) abrirPlayer('sb-' + String(n).padStart(3, '0'), String(n).padStart(3, '0') + ' — ' + p.titulo, true, 'banco'); };
window.tocarCell = cid => { const c = (DB.cells?.celulas_ritmicas || []).find(x => x.id === cid) || {}; abrirPlayer('cell-' + cid, 'Célula ' + cid + ' — ' + (c.nome || ''), false, 'vocab'); };

/* ---------- roteador ---------- */
function ir(t) {
  pararSynth();
  if (t !== 'metronomo' && M.on) pararMetro();
  document.querySelectorAll('.abas button').forEach(b => b.classList.toggle('ativa', b.dataset.tela === t));
  ({ trilha: telaTrilha, banco: telaBanco, metronomo: metroTela, vocab: telaVocab }[t] || telaTrilha)();
  window.scrollTo(0, 0);
}
window.ir = ir; window.verPeca = verPeca; window.setProg = setProg;
document.querySelectorAll('.abas button').forEach(b => b.onclick = () => ir(b.dataset.tela));

if ('serviceWorker' in navigator) navigator.serviceWorker.register('./sw.js').catch(() => {});
carregar().then(() => ir('trilha')).catch(() => { tela.innerHTML = '<p class="carregando">erro ao carregar os dados.</p>'; });
